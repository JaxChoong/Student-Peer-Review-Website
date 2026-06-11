class Group < ApplicationRecord
  belongs_to :course
  belongs_to :section

  has_many :group_memberships, dependent: :destroy
  has_many :members, through: :group_memberships, source: :user
  has_many :reviews, dependent: :destroy
  has_one :final_group_mark, dependent: :destroy

  validates :group_name, presence: true
end
