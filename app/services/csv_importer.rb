require 'csv'
require 'securerandom'

class CsvImporter
  # Input: course object, filepath
  # Returns: { success: true/false, error: string_message, new_users: array_of_arrays }
  def self.call(course:, filepath:)
    new_users = []
    
    # Expected headers: email, studentId, name, section, group
    begin
      csv = CSV.read(filepath, headers: true, encoding: "bom|utf-8")
      
      # Basic validation of headers
      required_headers = ['email', 'name', 'section', 'group']
      actual_headers = csv.headers.map { |h| h.to_s.downcase.strip }
      missing = required_headers - actual_headers
      return { success: false, error: "Missing headers: #{missing.join(', ')}. Found: #{actual_headers.join(', ')}" } if missing.any?
      
      ActiveRecord::Base.transaction do
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
          
          # Ensure section dates match course dates if newly created or missing dates
          section.update!(start_date: course.start_date, end_date: course.end_date) if section.start_date.nil? || section.end_date.nil?

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
      
      { success: true, new_users: new_users }
    rescue CSV::MalformedCSVError => e
      { success: false, error: "Invalid CSV format: #{e.message}" }
    rescue => e
      { success: false, error: e.message }
    end
  end
end
