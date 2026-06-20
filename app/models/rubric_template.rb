class RubricTemplate < ApplicationRecord
  belongs_to :user, optional: true
  has_many :rubric_criteria, -> { order(:position) }, class_name: "RubricCriteria", dependent: :destroy
  has_many :courses, dependent: :nullify

  validates :template_name, presence: true

  def max_possible_score
    rubric_criteria.sum { |c| c.rubric_columns.maximum(:weight).to_i }
  end
end
