class CreateLecturerRatings < ActiveRecord::Migration[8.1]
  def change
    create_table :lecturer_ratings do |t|
      t.references :lecturer, null: false, foreign_key: { to_table: :users }
      t.references :student, null: false, foreign_key: { to_table: :users }
      t.references :section, null: false, foreign_key: true
      t.decimal :rating, precision: 5, scale: 2

      t.timestamps
    end
    add_index :lecturer_ratings, [:lecturer_id, :student_id, :section_id], unique: true, name: 'index_lecturer_ratings_on_unique_rating'
  end
end
