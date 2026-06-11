class GroupMembership < ApplicationRecord
  belongs_to :group
  belongs_to :user

  validates :user_id, uniqueness: { scope: :group_id, message: "is already a member of this group" }
end
