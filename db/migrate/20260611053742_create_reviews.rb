class CreateReviews < ActiveRecord::Migration[8.1]
  def change
    create_table :reviews do |t|
      t.references :course, null: false, foreign_key: true
      t.references :section, null: false, foreign_key: true
      t.references :group, null: false, foreign_key: true
      t.references :reviewer, null: false, foreign_key: { to_table: :users }
      t.references :reviewee, null: false, foreign_key: { to_table: :users }
      t.decimal :score, precision: 5, scale: 2, null: false
      t.text :comment

      t.timestamps
    end
    add_index :reviews, [:course_id, :section_id, :group_id, :reviewer_id, :reviewee_id], unique: true, name: 'index_reviews_on_unique_review'
  end
end
