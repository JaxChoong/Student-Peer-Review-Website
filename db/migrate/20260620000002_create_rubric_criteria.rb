class CreateRubricCriteria < ActiveRecord::Migration[8.1]
  def change
    create_table :rubric_criteria do |t|
      t.references :rubric_template, null: false, foreign_key: true
      t.string :label, null: false
      t.integer :position, null: false, default: 0

      t.timestamps
    end
  end
end
