class Course < ApplicationRecord
  belongs_to :lecturer, class_name: 'User'
  belongs_to :question_layout, optional: true
  belongs_to :introduction, optional: true

  has_many :sections, dependent: :destroy
  has_many :groups, dependent: :destroy
  has_many :enrollments, dependent: :destroy
  has_many :students, through: :enrollments, source: :user
  has_many :reviews, dependent: :destroy
  has_many :self_assessments, dependent: :destroy

  validates :course_code, presence: true, uniqueness: true
  validates :course_name, presence: true
end
