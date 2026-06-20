class CreateRubricScores < ActiveRecord::Migration[8.1]
  def change
    create_table :rubric_scores do |t|
      t.references :review, null: false, foreign_key: true
      t.references :rubric_criteria, null: true, foreign_key: true
      t.string :criteria_label_snapshot, null: false
      t.integer :selected_weight, null: false
      t.integer :position, null: false, default: 0

      t.timestamps
    end
  end
end
