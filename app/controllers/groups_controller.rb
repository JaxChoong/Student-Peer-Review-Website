class GroupsController < ApplicationController
  before_action :require_lecturer

  def index
    @course = current_user.courses.find_by(id: params[:course_id])
    return redirect_to dashboard_path, alert: "Course not found." unless @course

    # Eager load groups and members for performance
    @groups = @course.groups.includes(:members, :section).order('sections.section_code', 'groups.group_name')
    @sections = @course.sections.order(:section_code)
  end

  def show
    @course = current_user.courses.find_by(id: params[:course_id])
    return redirect_to dashboard_path, alert: "Course not found." unless @course

    @group = @course.groups.includes(:members, :reviews, :final_group_mark).find_by(id: params[:id])
    return redirect_to course_groups_path(@course), alert: "Group not found." unless @group
  end
end
