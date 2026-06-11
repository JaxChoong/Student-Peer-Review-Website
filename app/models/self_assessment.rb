class SelfAssessment < ApplicationRecord
  belongs_to :course
  belongs_to :question
  belongs_to :user

  validates :user_id, uniqueness: { scope: [:course_id, :question_id], message: "has already submitted an assessment for this question" }
  validates :question_text, presence: true
  validates :answer, presence: true
end
