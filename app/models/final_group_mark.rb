class FinalGroupMark < ApplicationRecord
  belongs_to :group

  validates :mark, numericality: { greater_than_or_equal_to: 0, less_than_or_equal_to: 100 }, allow_nil: true
  validates :group_id, uniqueness: true
end
