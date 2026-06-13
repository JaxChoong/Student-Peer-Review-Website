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

    # Fetch questions
    @layout = @course.question_layout || QuestionLayout.where(user_id: nil).first
    @questions = @layout&.questions || []
    
    if @questions.empty?
      return redirect_to dashboard_path, alert: "No questions configured for this peer review."
    end

    @members = @group.members.where.not(id: current_user.id)
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

    ActiveRecord::Base.transaction do
      # 1. Process Self Assessments (Answers to Questions)
      if params[:answers].present?
        params[:answers].each do |question_id, answer|
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

      # 2. Process Peer Reviews
      # params[:reviews] expected format: { reviewee_id: { score: "3", comment: "Good job" }, ... }
      if params[:reviews].present?
        # To calculate adjusted ratings, we need the sum of all scores given by this reviewer
        # and the total number of students they reviewed.
        # However, the formula AdjR = (rating / total_ratings) * 3 * num_students usually means:
        # total_ratings = sum of all ratings given by reviewer to everyone
        # num_students = number of members in group excluding reviewer
        
        # Parse inputs
        raw_reviews = params[:reviews].permit!.to_h
        total_raw_score = raw_reviews.values.sum { |r| r[:score].to_i }
        num_students = @group.members.count - 1 # excluding self

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
    end

    redirect_to dashboard_path, notice: "Your peer review has been submitted successfully."
  rescue => e
    redirect_to dashboard_path, alert: "An error occurred while submitting your review: #{e.message}"
  end
end
