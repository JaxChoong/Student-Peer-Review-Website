class SectionsController < ApplicationController
  before_action :require_lecturer

  def update_review_dates
    @section = Section.find_by(id: params[:id])
    
    # Ensure the current user owns the course this section belongs to
    unless @section && @section.course.lecturer_id == current_user.id
      return redirect_to dashboard_path, alert: "Section not found."
    end

    if @section.update(start_date: params[:start_date], end_date: params[:end_date])
      redirect_to course_groups_path(@section.course), notice: "Review dates updated for section #{@section.section_code}."
    else
      redirect_to course_groups_path(@section.course), alert: "Failed to update review dates."
    end
  end
end
