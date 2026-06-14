class AddPendingCredentialsCsvToCourses < ActiveRecord::Migration[8.1]
  def change
    add_column :courses, :pending_credentials_csv, :text
  end
end
