class MarksController < ApplicationController
  before_action :require_lecturer

  def index
    @course = current_user.courses.find_by(id: params[:course_id])
    return redirect_to dashboard_path, alert: "Course not found." unless @course

    @total_groups = @course.groups.count
    @groups_with_marks = FinalGroupMark.where(group: @course.groups).count

    # Pre-calculate marks for all enrolled students
    @student_marks = []
    
      @course.sections.includes(enrollments: :user).each do |section|
      section.enrollments.each do |enrollment|
        student = enrollment.user
        group = student.groups.find_by(section: section)

        if group
          rubric_max = @course.rubric_scoring? ? @course.rubric_template&.max_possible_score : nil
          result = FinalMarkCalculator.call(student: student, group: group, rubric_max: rubric_max)
          @student_marks << {
            student: student,
            section: section,
            group: group,
            result: result
          }
        end
      end
    end
  end

  def export_template
    @course = current_user.courses.find_by(id: params[:course_id])
    
    require 'csv'
    csv_data = CSV.generate(headers: true) do |csv|
      csv << ["Student Email", "Student Name", "Section Code", "Group Name", "Group Mark", "Lecturer Rating"]
      
      @course.sections.includes(enrollments: :user).each do |section|
        section.enrollments.each do |enrollment|
          student = enrollment.user
          group = student.groups.find_by(section: section)
          if group
            group_mark = group.final_group_mark&.mark
            le = LecturerRating.find_by(student: student, section: section)&.rating
            csv << [student.email, student.name, section.section_code, group.group_name, group_mark, le]
          end
        end
      end
    end

    send_data csv_data, filename: "course_#{@course.course_code}_marks_template.csv"
  end

  def import
    @course = current_user.courses.find_by(id: params[:course_id])
    
    if params[:file].blank?
      return redirect_to course_marks_path(@course), alert: "Please upload a CSV file."
    end

    require 'csv'
    begin
      processed_count = 0
      ActiveRecord::Base.transaction do
        CSV.foreach(params[:file].path, headers: true) do |row|
          email = row["Student Email"]
          am = row["Group Mark"]
          le = row["Lecturer Rating"]

          student = User.find_by(email: email)
          next unless student

          # Find the group for this student in this course
          group = student.groups.find_by(course_id: @course.id)
          next unless group

          # Save AM (FinalGroupMark)
          if am.present?
            fgm = FinalGroupMark.find_or_initialize_by(group: group)
            fgm.mark = am.to_f
            fgm.save!
          end

          # Save LE (LecturerRating)
          if le.present?
            rating = LecturerRating.find_or_initialize_by(
              lecturer: current_user,
              student: student,
              section: group.section
            )
            rating.rating = le.to_f
            rating.save!
          end
          
          processed_count += 1 if am.present? || le.present?
        end
      end
      
      if processed_count > 0
        redirect_to course_marks_path(@course), notice: "Marks imported successfully for #{processed_count} students."
      else
        redirect_to course_marks_path(@course), alert: "No marks were imported. Please ensure you are using the exact headers: 'Student Email', 'Group Mark', and 'Lecturer Rating'."
      end
    rescue => e
      redirect_to course_marks_path(@course), alert: "Error importing marks: #{e.message}"
    end
  end

  def export_final
    @course = current_user.courses.find_by(id: params[:course_id])
    
    if @course.hybrid? && !FinalGroupMark.where(group: @course.groups).exists?
      return redirect_to course_marks_path(@course), alert: "You must import lecturer marks before exporting final marks."
    end

    require 'csv'
    csv_data = CSV.generate(headers: true) do |csv|
      peer_score_label = @course.rubric_scoring? ? "Avg Total Rubric Score" : "Avg Peer Rating"

      # Build headers dynamically
      headers = ["Student ID", "Student Email", "Student Name", "Section", "Group"]
      headers << "Assignment Mark" unless @course.peer_ratings_only?
      headers << peer_score_label
      
      rubric_criteria_list = []
      if @course.rubric_scoring? && @course.rubric_template
        rubric_criteria_list = @course.rubric_template.rubric_criteria.order(:position)
        rubric_criteria_list.each do |crit|
          headers << "Avg: #{crit.label}"
        end
      end
      
      headers << "Lecturer Evaluation" unless @course.peer_ratings_only?
      headers << "Penalty"
      headers << "Final Calculated Mark" unless @course.peer_ratings_only?
      
      csv << headers
      
      @course.sections.includes(enrollments: :user).each do |section|
        section.enrollments.each do |enrollment|
          student = enrollment.user
          group = student.groups.find_by(section: section)
          
          if group
            rubric_max = @course.rubric_scoring? ? @course.rubric_template&.max_possible_score : nil
            result = FinalMarkCalculator.call(student: student, group: group, rubric_max: rubric_max)
            
            row = [
              student.student_number, 
              student.email, 
              student.name, 
              section.section_code, 
              group.group_name
            ]
            
            row << sprintf("%.2f", result[:am]) unless @course.peer_ratings_only?
            row << sprintf("%.2f", result[:apr])
            
            if @course.rubric_scoring? && @course.rubric_template
              reviews_received = Review.where(reviewee: student, group: group)
              review_ids = reviews_received.select(:id)
              
              rubric_criteria_list.each do |crit|
                if reviews_received.any?
                  total_crit_score = RubricScore.where(review_id: review_ids, rubric_criteria_id: crit.id).sum(:selected_weight)
                  avg_crit_score = total_crit_score.to_f / reviews_received.count
                  row << sprintf("%.2f", avg_crit_score)
                else
                  row << "0.00"
                end
              end
            end
            
            row << sprintf("%.2f", result[:le]) unless @course.peer_ratings_only?
            row << (result[:penalty] ? "YES" : "NO")
            row << sprintf("%.2f", result[:final_mark]) unless @course.peer_ratings_only?
            
            csv << row
          end
        end
      end
    end

    send_data csv_data, filename: "course_#{@course.course_code}_final_marks.csv"
  end
end
