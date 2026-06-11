class CreateEnrollments < ActiveRecord::Migration[8.1]
  def change
    create_table :enrollments do |t|
      t.references :course, null: false, foreign_key: true
      t.references :section, null: false, foreign_key: true
      t.references :user, null: false, foreign_key: true

      t.timestamps
    end
    add_index :enrollments, [:course_id, :section_id, :user_id], unique: true
  end
end
