class RubricColumn < ApplicationRecord
  belongs_to :rubric_criteria

  validates :weight, presence: true, numericality: { only_integer: true }
  validates :position, numericality: { only_integer: true, greater_than_or_equal_to: 0 }
  validate  :column_count_within_limit

  private

  def column_count_within_limit
    return unless rubric_criteria
    existing = rubric_criteria.rubric_columns.where.not(id: id).count
    errors.add(:base, "A criteria row cannot have more than 10 columns") if existing >= 10
  end
end
