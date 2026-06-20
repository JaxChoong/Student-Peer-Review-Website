class RubricScore < ApplicationRecord
  belongs_to :review
  belongs_to :rubric_criteria, optional: true

  validates :criteria_label_snapshot, presence: true
  validates :selected_weight, presence: true, numericality: { only_integer: true }
end
