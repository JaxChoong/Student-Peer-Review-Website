class AddRequireSelfReviewToCourses < ActiveRecord::Migration[8.1]
  def change
    add_column :courses, :require_self_review, :boolean, default: true, null: false
  end
end
