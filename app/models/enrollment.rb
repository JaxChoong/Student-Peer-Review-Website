class Enrollment < ApplicationRecord
  belongs_to :course
  belongs_to :section
  belongs_to :user

  validates :user_id, uniqueness: { scope: [:course_id, :section_id], message: "is already enrolled in this section of the course" }
end
