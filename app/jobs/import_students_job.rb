class ImportStudentsJob < ApplicationJob
  queue_as :default

  def perform(course, filepath, user_id)
    begin
      result = CsvImporter.call(
        course: course,
        filepath: filepath
      )

      if result[:success]
        if result[:new_users].any?
          csv_string = CSV.generate do |csv|
            csv << ["Email", "Name", "Temporary Password"]
            result[:new_users].each do |user_data|
              csv << user_data
            end
          end
          course.update(pending_credentials_csv: csv_string)
        end

        ActionCable.server.broadcast(
          "notifications_#{user_id}",
          { type: "notice", message: "Students imported successfully!" }
        )
      else
        ActionCable.server.broadcast(
          "notifications_#{user_id}",
          { type: "alert", message: "Error importing students: #{result[:error]}" }
        )
      end
    rescue => e
      ActionCable.server.broadcast(
        "notifications_#{user_id}",
        { type: "alert", message: "Error processing file: #{e.message}" }
      )
    ensure
      # Clean up the persistent temporary file to prevent disk space leaks
      File.delete(filepath) if File.exist?(filepath)
    end
  end
end
