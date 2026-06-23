class PeerReviewsController < ApplicationController
  before_action :require_student

  def start
    @course = current_user.enrolled_courses.find_by(id: params[:course_id])
    return redirect_to dashboard_path, alert: "Course not found." unless @course

    # Get the group the student belongs to in this course
    @group = current_user.groups.find_by(course_id: @course.id)
    return redirect_to dashboard_path, alert: "You are not assigned to a group for this course." unless @group

    @section = @group.section

    # Check review dates
    status, message = ReviewDateChecker.call(@section)
    if status != :open
      return redirect_to dashboard_path, alert: message
    end

    # Check if already submitted
    if Review.exists?(reviewer: current_user, course: @course) || SelfAssessment.exists?(user: current_user, course: @course)
      return redirect_to dashboard_path, alert: "You have already submitted your peer review for this course."
    end

    # Fetch questions
    @layout = @course.question_layout || QuestionLayout.where(user_id: nil).first
    @questions = @layout&.questions || []
    
    if !@course.peer_ratings_only? && @questions.empty? && @course.require_self_review?
      # Self assessment questions required for hybrid mode
      return redirect_to dashboard_path, alert: "No questions configured for this peer review."
    end

    if @course.rubric_scoring?
      @rubric_template = @course.rubric_template
      unless @rubric_template
        return redirect_to dashboard_path, alert: "No rubric template is configured for this course."
      end
    end

    @members = @group.members.order(:id)
  end

  def submit
    @course = current_user.enrolled_courses.find_by(id: params[:course_id])
    return redirect_to dashboard_path, alert: "Course not found." unless @course

    @group = current_user.groups.find_by(course_id: @course.id)
    return redirect_to dashboard_path, alert: "You are not assigned to a group for this course." unless @group

    @section = @group.section

    # Re-verify review dates
    status, message = ReviewDateChecker.call(@section)
    if status != :open
      return redirect_to dashboard_path, alert: message
    end

    # Check if already submitted
    if Review.exists?(reviewer: current_user, course: @course) || SelfAssessment.exists?(user: current_user, course: @course)
      return redirect_to dashboard_path, alert: "You have already submitted your peer review for this course."
    end

    ActiveRecord::Base.transaction do
      process_self_assessments(params[:answers]) if params[:answers].present? && @course.require_self_review?

      if @course.rubric_scoring?
        process_rubric_reviews(params[:rubric_reviews]) if params[:rubric_reviews].present?
      else
        process_numeric_reviews(params[:reviews]) if params[:reviews].present?
      end
    end

    redirect_to dashboard_path, notice: "Your peer review has been submitted successfully."
  rescue => e
    redirect_to dashboard_path, alert: "An error occurred while submitting your review: #{e.message}"
  end

  private

  def process_self_assessments(answers)
    answers.each do |question_id, answer|
      question = Question.find_by(id: question_id)
      next unless question

      sa = SelfAssessment.find_or_initialize_by(
        course: @course,
        question: question,
        user: current_user
      )
      sa.question_text = question.question_text
      sa.answer = answer
      sa.save!
    end
  end

  def process_numeric_reviews(reviews_param)
    raw_reviews = params.require(:reviews).permit(reviews_param.keys.map { |id| { id => [:score, :comment] } }).to_h
    total_raw_score = raw_reviews.values.sum { |r| r[:score].to_i }
    num_students = @group.members.count

    raw_reviews.each do |reviewee_id, data|
      score = data[:score].to_i
      comment = data[:comment]

      adjusted_score = AdjustedRatingCalculator.call(
        rating: score,
        total_ratings: total_raw_score,
        num_students: num_students
      )

      review = Review.find_or_initialize_by(
        course: @course,
        section: @section,
        group: @group,
        reviewer: current_user,
        reviewee_id: reviewee_id
      )
      review.score = adjusted_score
      review.comment = comment
      review.save!
    end
  end

  def process_rubric_reviews(rubric_param)
    # params structure: { reviewee_id => { criteria_id => { weight: 3 } } }
    rubric_param.each do |reviewee_id, criteria_scores|
      total_score = criteria_scores.values.sum { |data| data[:weight].to_i }

      review = Review.find_or_initialize_by(
        course: @course,
        section: @section,
        group: @group,
        reviewer: current_user,
        reviewee_id: reviewee_id
      )
      review.score = total_score
      review.comment = "Rubric evaluation" # Minimal comment as rubrics don't have text feedback per user in UI
      review.save!

      criteria_scores.each do |criteria_id, data|
        criteria = RubricCriteria.find_by(id: criteria_id)
        next unless criteria
        
        RubricScore.create!(
          review: review,
          rubric_criteria_id: criteria.id,
          criteria_label_snapshot: criteria.label,
          selected_weight: data[:weight].to_i,
          position: criteria.position
        )
      end
    end
  end
end
