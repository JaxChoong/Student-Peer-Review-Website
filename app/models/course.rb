class Course < ApplicationRecord
  belongs_to :lecturer, class_name: 'User'
  belongs_to :question_layout, optional: true
  belongs_to :rubric_template, optional: true
  belongs_to :introduction, optional: true

  has_many :sections, dependent: :destroy
  has_many :groups, dependent: :destroy
  has_many :enrollments, dependent: :destroy
  has_many :students, through: :enrollments, source: :user
  has_many :reviews, dependent: :destroy
  has_many :self_assessments, dependent: :destroy

  validates :course_code, presence: true, uniqueness: true
  validates :course_name, presence: true
  validates :review_mode, presence: true

  enum :review_mode, {
    peer_ratings_only: 0,
    hybrid: 1
  }, default: :peer_ratings_only

  enum :scoring_scheme, {
    numeric: 0,
    rubric: 1,
    point_pool: 2
  }, default: :numeric

  def rubric_scoring?
    rubric?
  end

  def review_started?
    return true if start_date && Date.today >= start_date
    return true if reviews.exists? || self_assessments.exists?
    false
  end
end
