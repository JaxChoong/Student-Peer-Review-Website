class MarksController < ApplicationController
  before_action :require_lecturer

  def index
    @course = current_user.courses.find_by(id: params[:course_id])
    return redirect_to dashboard_path, alert: "Course not found." unless @course

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
      csv << ["student_email", "student_name", "section_code", "group_name", "group_mark_am", "lecturer_rating_le"]
      
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
      ActiveRecord::Base.transaction do
        CSV.foreach(params[:file].path, headers: true) do |row|
          email = row["student_email"]
          am = row["group_mark_am"]
          le = row["lecturer_rating_le"]

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
        end
      end
      redirect_to course_marks_path(@course), notice: "Marks imported successfully."
    rescue => e
      redirect_to course_marks_path(@course), alert: "Error importing marks: #{e.message}"
    end
  end

  def export_final
    @course = current_user.courses.find_by(id: params[:course_id])
    
    require 'csv'
    csv_data = CSV.generate(headers: true) do |csv|
      csv << ["student_id", "student_email", "student_name", "section", "group", "assignment_mark", "avg_peer_rating", "lecturer_evaluation", "penalty", "final_calculated_mark"]
      
      @course.sections.includes(enrollments: :user).each do |section|
        section.enrollments.each do |enrollment|
          student = enrollment.user
          group = student.groups.find_by(section: section)
          
          if group
            result = FinalMarkCalculator.call(student: student, group: group)
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

    send_data csv_data, filename: "course_#{@course.course_code}_final_marks.csv"
  end
end
