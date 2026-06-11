require 'rails_helper'

RSpec.describe GroupMembership, type: :model do
  describe 'validations' do
    subject { build(:group_membership) }
    it { should validate_uniqueness_of(:user_id).scoped_to(:group_id).with_message('is already a member of this group') }
  end

  describe 'associations' do
    it { should belong_to(:group) }
    it { should belong_to(:user) }
  end
end
