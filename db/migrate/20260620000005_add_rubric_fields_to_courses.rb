class AddRubricFieldsToCourses < ActiveRecord::Migration[8.1]
  def change
    add_reference :courses, :rubric_template, null: true, foreign_key: true
    add_column :courses, :scoring_scheme, :integer, null: false, default: 0
  end
end
