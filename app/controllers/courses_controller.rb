class CoursesController < ApplicationController
  before_action :require_lecturer

  def new
    @course = Course.new
  end

  def create
    if params[:file].blank?
      redirect_to new_course_path, alert: "Please upload a CSV file."
      return
    end

    # This will be replaced by the actual CsvImporter service
    begin
      result = CsvImporter.call(
        lecturer_id: current_user.id,
        filepath: params[:file].path
      )
      
      if result[:success]
        flash[:notice] = "Course created successfully!"
        # If new students were created with temp passwords, we could send that CSV back here
        redirect_to dashboard_path
      else
        redirect_to new_course_path, alert: "Error importing course: #{result[:error]}"
      end
    rescue => e
      redirect_to new_course_path, alert: "Error processing file: #{e.message}"
    end
  end

  def destroy
    @course = current_user.courses.find_by(id: params[:id])
    if @course
      @course.destroy
      redirect_to dashboard_path, notice: "Course deleted successfully."
    else
      redirect_to dashboard_path, alert: "Course not found."
    end
  end

  def update_intro
    @course = current_user.courses.find_by(id: params[:id])
    return redirect_to dashboard_path, alert: "Course not found." unless @course

    # Simple logic for updating intro
    intro = Introduction.find_or_create_by(content: params[:content])
    @course.update(introduction: intro)
    
    redirect_to course_groups_path(@course), notice: "Course introduction updated."
  end

  def update_review_dates
    @course = current_user.courses.find_by(id: params[:id])
    return redirect_to dashboard_path, alert: "Course not found." unless @course

    if @course.update(start_date: params[:start_date], end_date: params[:end_date])
      # Update all sections to match the course dates
      @course.sections.update_all(start_date: params[:start_date], end_date: params[:end_date])
      redirect_to course_groups_path(@course), notice: "Review dates updated for all sections."
    else
      redirect_to course_groups_path(@course), alert: "Failed to update review dates."
    end
  end

  def update_layout
    @course = current_user.courses.find_by(id: params[:id])
    return redirect_to dashboard_path, alert: "Course not found." unless @course

    if @course.update(question_layout_id: params[:question_layout_id])
      redirect_to course_groups_path(@course), notice: "Question layout updated."
    else
      redirect_to course_groups_path(@course), alert: "Failed to update question layout."
    end
  end
end
