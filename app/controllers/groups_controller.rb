class GroupsController < ApplicationController
  before_action :require_lecturer

  def index
    @course = current_user.courses.find_by(id: params[:course_id])
    return redirect_to dashboard_path, alert: "Course not found." unless @course

    # Eager load groups and members for performance
    @groups = @course.groups.includes(:members, :section).order('sections.section_code', 'groups.group_name')
    @sections = @course.sections.order(:section_code)
    
    # Fetch all reviewer IDs who have submitted reviews in this course to show green dots
    @submitted_reviewer_ids = Review.where(course: @course).pluck(:reviewer_id).uniq.to_set
  end

  def show
    @course = current_user.courses.find_by(id: params[:course_id])
    return redirect_to dashboard_path, alert: "Course not found." unless @course

    @group = @course.groups.includes(:members, :reviews, :final_group_mark).find_by(id: params[:id])
    return redirect_to course_groups_path(@course), alert: "Group not found." unless @group

    # Pre-fetch all reviews for all members so we can build the tabbed interface
    @self_assessments = SelfAssessment.where(user: @group.members, course: @course).order(:id).group_by(&:user_id)
    @peer_reviews_given = Review.where(reviewer: @group.members, group: @group).includes(:reviewee).order(:id).group_by(&:reviewer_id)
  end
end
