class CreateCourses < ActiveRecord::Migration[8.1]
  def change
    create_table :courses do |t|
      t.string :course_code
      t.string :course_name
      t.references :lecturer, null: false, foreign_key: { to_table: :users }
      t.references :question_layout, null: true, foreign_key: true
      t.references :introduction, null: true, foreign_key: true
      t.date :start_date
      t.date :end_date

      t.timestamps
    end
    add_index :courses, :course_code, unique: true
  end
end
