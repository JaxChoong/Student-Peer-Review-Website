class QuestionLayout < ApplicationRecord
  belongs_to :user, optional: true

  has_many :questions, dependent: :destroy
  accepts_nested_attributes_for :questions, allow_destroy: true, reject_if: proc { |att| att['question_text'].blank? }
  has_many :courses, dependent: :nullify

  validates :layout_name, presence: true
end
