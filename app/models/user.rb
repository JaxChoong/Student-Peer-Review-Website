class User < ApplicationRecord
  has_secure_password

  enum :role, { student: 'student', lecturer: 'lecturer' }

  validates :email, presence: true, uniqueness: true, format: { with: URI::MailTo::EMAIL_REGEXP }
  validates :name, presence: true
  validates :role, presence: true
  validates :password, length: { minimum: 6 }, allow_nil: true
  has_many :courses, foreign_key: :lecturer_id, dependent: :destroy
  has_many :enrollments, dependent: :destroy
  has_many :enrolled_courses, through: :enrollments, source: :course
  has_many :group_memberships, dependent: :destroy
  has_many :groups, through: :group_memberships
  has_many :reviews_given, class_name: 'Review', foreign_key: :reviewer_id, dependent: :destroy
  has_many :reviews_received, class_name: 'Review', foreign_key: :reviewee_id, dependent: :destroy
  has_many :self_assessments, dependent: :destroy
  has_many :question_layouts, dependent: :destroy
  has_many :lecturer_ratings_given, class_name: 'LecturerRating', foreign_key: :student_id, dependent: :destroy
  has_many :lecturer_ratings_received, class_name: 'LecturerRating', foreign_key: :lecturer_id, dependent: :destroy
end
