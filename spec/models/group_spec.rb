require 'rails_helper'

RSpec.describe Group, type: :model do
  describe 'validations' do
    it { should validate_presence_of(:group_name) }
  end

  describe 'associations' do
    it { should belong_to(:course) }
    it { should belong_to(:section) }
    it { should have_many(:group_memberships).dependent(:destroy) }
    it { should have_many(:members).through(:group_memberships).source(:user) }
    it { should have_many(:reviews).dependent(:destroy) }
    it { should have_one(:final_group_mark).dependent(:destroy) }
  end
end
