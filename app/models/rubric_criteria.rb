class RubricCriteria < ApplicationRecord
  belongs_to :rubric_template
  has_many :rubric_columns, -> { order(:position) }, dependent: :destroy
  has_many :rubric_scores, dependent: :nullify

  validates :label, presence: true
  validates :position, numericality: { only_integer: true, greater_than_or_equal_to: 0 }
end
