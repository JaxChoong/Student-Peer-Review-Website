class Review < ApplicationRecord
  belongs_to :course
  belongs_to :section
  belongs_to :group
  belongs_to :reviewer, class_name: 'User'
  belongs_to :reviewee, class_name: 'User'

  validates :score, presence: true, numericality: { greater_than_or_equal_to: 0 }
  validates :reviewer_id, uniqueness: { scope: [:course_id, :section_id, :group_id, :reviewee_id], message: "has already reviewed this student for this assignment" }
end
