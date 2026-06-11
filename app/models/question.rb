class Question < ApplicationRecord
  belongs_to :question_layout

  has_many :self_assessments, dependent: :destroy

  validates :question_text, presence: true
end
