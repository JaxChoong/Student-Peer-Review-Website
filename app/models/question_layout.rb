class QuestionLayout < ApplicationRecord
  belongs_to :user, optional: true

  has_many :questions, dependent: :destroy
  has_many :courses, dependent: :nullify

  validates :layout_name, presence: true
end
