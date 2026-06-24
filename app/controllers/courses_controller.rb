class CoursesController < ApplicationController
  before_action :require_lecturer

  def new
    @course = Course.new
  end

  def create
    begin
      scheme = params[:scoring_scheme].present? ? params[:scoring_scheme].to_i : 0
      
      if params[:introduction].present?
        intro_record = Introduction.create!(content: params[:introduction])
      else
        intro_record = Introduction.first
      end

      course_params = {
        lecturer_id: current_user.id,
        course_code: params[:course_code],
        course_name: params[:course_name],
        start_date: params[:start_date],
        end_date: params[:end_date],
        introduction: intro_record,
        review_mode: params[:review_mode].present? ? params[:review_mode].to_i : 0,
        scoring_scheme: scheme,
        question_layout_id: QuestionLayout.find_by(user_id: nil)&.id,
        require_self_review: params[:require_self_review] == "1"
      }
      
      if scheme == 1
        course_params[:rubric_template_id] = RubricTemplate.find_by(user_id: nil)&.id
      end

      @course = Course.create!(course_params)
      flash[:notice] = "Course created successfully!"
      redirect_to course_groups_path(@course)
    rescue => e
      redirect_to new_course_path, alert: "Error creating course: #{e.message}"
    end
  end

  def import_students
    @course = current_user.courses.find_by(id: params[:id])
    return redirect_to dashboard_path, alert: "Course not found." unless @course

    if params[:file].blank?
      redirect_to course_groups_path(@course), alert: "Please upload a CSV file."
      return
    end

    begin
      result = CsvImporter.call(
        course: @course,
        filepath: params[:file].path
      )

      if result[:success]
        if result[:new_users].any?
          csv_string = CSV.generate do |csv|
            csv << ["Email", "Name", "Temporary Password"]
            result[:new_users].each do |user_data|
              csv << user_data
            end
          end
          @course.update(pending_credentials_csv: csv_string)
        end

        flash[:notice] = "Students imported successfully!"
        redirect_to course_groups_path(@course)
      else
        redirect_to course_groups_path(@course), alert: "Error importing students: #{result[:error]}"
      end
    rescue => e
      redirect_to course_groups_path(@course), alert: "Error processing file: #{e.message}"
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
    if params.key?(:require_self_review)
      update_params[:require_self_review] = params[:require_self_review] == "1"
    end
    update_params[:rubric_template_id] = params[:rubric_template_id] if @course.rubric_scoring?

    if @course.update(update_params)
      redirect_to course_groups_path(@course), notice: "Course templates updated successfully."
    else
      redirect_to course_groups_path(@course), alert: "Failed to update templates."
    end
  end



  def update_settings
    @course = current_user.courses.find_by(id: params[:id])
    return redirect_to dashboard_path, alert: "Course not found." unless @course

    if @course.review_started?
      redirect_to course_groups_path(@course), alert: "Settings are locked and cannot be changed after the review starts."
    else
      review_mode = params[:review_mode].to_i
      scoring_scheme = params[:scoring_scheme].to_i
      
      # Backend Enforcements
      if review_mode == 1 # hybrid
        scoring_scheme = 0 # numeric
      end
      
      update_params = {
        review_mode: review_mode,
        scoring_scheme: scoring_scheme
      }

      if @course.update(update_params)
        if @course.rubric_scoring? && @course.rubric_template_id.nil?
          default_rubric = RubricTemplate.where(user_id: nil).first
          @course.update(rubric_template_id: default_rubric.id) if default_rubric
        end
        redirect_to course_groups_path(@course), notice: "Course settings updated successfully."
      else
        redirect_to course_groups_path(@course), alert: "Failed to update settings."
      end
    end
  end
end
