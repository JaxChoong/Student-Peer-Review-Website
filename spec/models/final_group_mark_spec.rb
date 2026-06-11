require 'rails_helper'

RSpec.describe FinalGroupMark, type: :model do
  describe 'validations' do
    subject { build(:final_group_mark) }
    it { should validate_numericality_of(:mark).is_greater_than_or_equal_to(0).is_less_than_or_equal_to(100).allow_nil }
    it { should validate_uniqueness_of(:group_id) }
  end

  describe 'associations' do
    it { should belong_to(:group) }
  end
end
