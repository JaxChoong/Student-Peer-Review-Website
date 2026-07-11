class AddPenaltySettingsToCourses < ActiveRecord::Migration[8.1]
  def change
    add_column :courses, :apply_penalty, :boolean, default: true, null: false
    add_column :courses, :penalty_percentage, :integer, default: 100, null: false
  end
end
