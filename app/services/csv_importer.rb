require 'csv'
require 'securerandom'

class CsvImporter
  # Input: lecturer_id, filepath, course_code, course_name, start_date, end_date, introduction
  # Returns: { success: true/false, error: string_message, new_users: array_of_arrays, course: Course_object }
  def self.call(lecturer_id:, filepath:, course_code:, course_name:, start_date:, end_date:, introduction: nil, review_mode: nil, scoring_scheme: nil)
    new_users = []
    
    # Expected headers: email, studentId, name, section, group
    begin
      csv = CSV.read(filepath, headers: true, encoding: "bom|utf-8")
      
      # Basic validation of headers
      required_headers = ['email', 'name', 'section', 'group']
      actual_headers = csv.headers.map { |h| h.to_s.downcase.strip }
      missing = required_headers - actual_headers
      return { success: false, error: "Missing headers: #{missing.join(', ')}. Found: #{actual_headers.join(', ')}" } if missing.any?
      
      course = nil
      ActiveRecord::Base.transaction do
        if introduction.present?
          intro_record = Introduction.create!(content: introduction)
        else
          intro_record = Introduction.first
        end

        scheme = scoring_scheme.present? ? scoring_scheme.to_i : 0
        
        course_params = {
          lecturer_id: lecturer_id,
          course_code: course_code,
          course_name: course_name,
          start_date: start_date,
          end_date: end_date,
          introduction: intro_record,
          review_mode: review_mode.present? ? review_mode.to_i : 0,
          scoring_scheme: scheme,
          question_layout_id: QuestionLayout.find_by(user_id: nil)&.id
        }
        
        if scheme == 1
          course_params[:rubric_template_id] = RubricTemplate.find_by(user_id: nil)&.id
        end

        course = Course.create!(course_params)

        csv.each do |row|
          row_hash = row.to_h.transform_keys { |k| k.to_s.downcase.strip }
          
          email = row_hash['email']
          name = row_hash['name']
          student_number = row_hash['studentid'] || row_hash['student_id'] || row_hash['student number']
          section_code = row_hash['section']
          group_name = row_hash['group']

          # Find or Create User
          user = User.find_by(email: email)
          unless user
            temp_password = SecureRandom.hex(6)
            user = User.create!(
              email: email,
              name: name,
              student_number: student_number,
              role: 'student',
              password: temp_password,
              password_confirmation: temp_password
            )
            new_users << [email, name, temp_password]
          end

          # Find or Create Section
          section = Section.find_or_create_by!(
            course: course,
            section_code: section_code
          )
          
          # Update section dates to match course dates
          section.update!(start_date: start_date, end_date: end_date)

          # Find or Create Group
          group = Group.find_or_create_by!(
            course: course,
            section: section,
            group_name: group_name
          )

          # Find or Create Enrollment
          Enrollment.find_or_create_by!(
            course: course,
            section: section,
            user: user
          )

          # Find or Create GroupMembership
          GroupMembership.find_or_create_by!(
            group: group,
            user: user
          )
        end
      end
      
      { success: true, new_users: new_users, course: course }
    rescue CSV::MalformedCSVError => e
      { success: false, error: "Invalid CSV format: #{e.message}" }
    rescue => e
      { success: false, error: e.message }
    end
  end
end
