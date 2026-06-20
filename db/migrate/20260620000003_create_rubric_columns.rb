class CreateRubricColumns < ActiveRecord::Migration[8.1]
  def change
    create_table :rubric_columns do |t|
      t.references :rubric_criteria, null: false, foreign_key: true
      t.integer :weight, null: false
      t.integer :position, null: false, default: 0
      t.text :descriptions, array: true, default: []

      t.timestamps
    end
  end
end
