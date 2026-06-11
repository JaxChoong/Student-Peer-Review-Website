class LecturerRating < ApplicationRecord
  belongs_to :lecturer, class_name: 'User'
  belongs_to :student, class_name: 'User'
  belongs_to :section

  validates :rating, numericality: { greater_than_or_equal_to: 0, less_than_or_equal_to: 3 }, allow_nil: true
  validates :lecturer_id, uniqueness: { scope: [:student_id, :section_id] }
end
