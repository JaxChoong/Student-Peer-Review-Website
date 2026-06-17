class AddReviewModeToCourses < ActiveRecord::Migration[8.1]
  def change
    add_column :courses, :review_mode, :integer, default: 0, null: false
  end
end
