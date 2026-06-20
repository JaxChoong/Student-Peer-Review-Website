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

    begin
      result = CsvImporter.call(
        lecturer_id: current_user.id,
        filepath: params[:file].path,
        course_code: params[:course_code],
        course_name: params[:course_name],
        start_date: params[:start_date],
        end_date: params[:end_date],
        introduction: params[:introduction],
        review_mode: params[:review_mode],
        scoring_scheme: params[:scoring_scheme]
      )

      if result[:success]
        course = result[:course]
        if result[:new_users].any?
          csv_string = CSV.generate do |csv|
            csv << ["Email", "Name", "Temporary Password"]
            result[:new_users].each do |user_data|
              csv << user_data
            end
          end
          course.update(pending_credentials_csv: csv_string)
        end

        flash[:notice] = "Course created successfully!"
        redirect_to course_groups_path(course)
      else
        redirect_to new_course_path, alert: "Error importing course: #{result[:error]}"
      end
    rescue => e
      redirect_to new_course_path, alert: "Error processing file: #{e.message}"
    end
  end

  def download_credentials
    @course = current_user.courses.find_by(id: params[:id])
    if @course && @course.pending_credentials_csv.present?
      csv_data = @course.pending_credentials_csv
      @course.update(pending_credentials_csv: nil)
      send_data csv_data, filename: "temp_user_creds.csv", type: "text/csv", disposition: "attachment"
    else
      redirect_to dashboard_path, alert: "Credentials not found or already downloaded."
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

    update_params = { question_layout_id: params[:question_layout_id] }
    update_params[:rubric_template_id] = params[:rubric_template_id] if @course.rubric_scoring?

    if @course.update(update_params)
      redirect_to course_groups_path(@course), notice: "Course templates updated successfully."
    else
      redirect_to course_groups_path(@course), alert: "Failed to update templates."
    end
  end

  def update_review_mode
    @course = current_user.courses.find_by(id: params[:id])
    return redirect_to dashboard_path, alert: "Course not found." unless @course

    if @course.review_started?
      redirect_to course_groups_path(@course), alert: "Review mode is locked and cannot be changed after the review starts."
    else
      if @course.update(review_mode: params[:review_mode].to_i)
        redirect_to course_groups_path(@course), notice: "Review mode updated successfully."
      else
        redirect_to course_groups_path(@course), alert: "Failed to update review mode."
      end
    end
  end

  def update_rubric_template
    @course = current_user.courses.find_by(id: params[:id])
    return redirect_to dashboard_path, alert: "Course not found." unless @course

    if @course.update(rubric_template_id: params[:rubric_template_id])
      redirect_to course_groups_path(@course), notice: "Rubric template updated."
    else
      redirect_to course_groups_path(@course), alert: "Failed to update rubric template."
    end
  end

  def update_scoring_scheme
    @course = current_user.courses.find_by(id: params[:id])
    return redirect_to dashboard_path, alert: "Course not found." unless @course

    if @course.review_started?
      redirect_to course_groups_path(@course), alert: "Scoring scheme cannot be changed after the review starts."
    else
      if @course.update(scoring_scheme: params[:scoring_scheme].to_i)
        redirect_to course_groups_path(@course), notice: "Scoring scheme updated."
      else
        redirect_to course_groups_path(@course), alert: "Failed to update scoring scheme."
      end
    end
  end
end
