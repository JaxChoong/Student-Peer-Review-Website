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
          result = FinalMarkCalculator.call(student: student, group: group)
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
      if @course.peer_ratings_only?
        csv << ["Student ID", "Student Email", "Student Name", "Section", "Group", "Avg Peer Rating", "Penalty"]
      else
        csv << ["Student ID", "Student Email", "Student Name", "Section", "Group", "Assignment Mark", "Avg Peer Rating", "Lecturer Evaluation", "Penalty", "Final Calculated Mark"]
      end
      
      @course.sections.includes(enrollments: :user).each do |section|
        section.enrollments.each do |enrollment|
          student = enrollment.user
          group = student.groups.find_by(section: section)
          
          if group
            result = FinalMarkCalculator.call(student: student, group: group)
            if @course.peer_ratings_only?
              csv << [
                student.student_number, 
                student.email, 
                student.name, 
                section.section_code, 
                group.group_name,
                result[:apr],
                result[:penalty] ? "YES" : "NO"
              ]
            else
              csv << [
                student.student_number, 
                student.email, 
                student.name, 
                section.section_code, 
                group.group_name,
                result[:am],
                result[:apr],
                result[:le],
                result[:penalty] ? "YES" : "NO",
                result[:final_mark]
              ]
            end
          end
        end
      end
    end

    send_data csv_data, filename: "course_#{@course.course_code}_final_marks.csv"
  end
end
