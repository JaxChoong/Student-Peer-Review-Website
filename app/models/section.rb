class Section < ApplicationRecord
  belongs_to :course

  has_many :groups, dependent: :destroy
  has_many :enrollments, dependent: :destroy
  has_many :students, through: :enrollments, source: :user
  has_many :reviews, dependent: :destroy
  has_many :lecturer_ratings, dependent: :destroy

  validates :section_code, presence: true
end
