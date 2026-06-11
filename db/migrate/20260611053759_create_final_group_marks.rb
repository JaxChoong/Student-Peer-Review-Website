class CreateFinalGroupMarks < ActiveRecord::Migration[8.1]
  def change
    create_table :final_group_marks do |t|
      t.references :group, null: false, foreign_key: true, index: { unique: true }
      t.decimal :mark, precision: 6, scale: 2

      t.timestamps
    end
  end
end
