require 'rails_helper'

RSpec.describe Review, type: :model do
  describe 'validations' do
    subject { build(:review) }
    it { should validate_presence_of(:score) }
    it { should validate_numericality_of(:score).is_greater_than_or_equal_to(0) }
    it { should validate_uniqueness_of(:reviewer_id).scoped_to(:course_id, :section_id, :group_id, :reviewee_id).with_message('has already reviewed this student for this assignment') }
  end

  describe 'associations' do
    it { should belong_to(:course) }
    it { should belong_to(:section) }
    it { should belong_to(:group) }
    it { should belong_to(:reviewer).class_name('User') }
    it { should belong_to(:reviewee).class_name('User') }
  end
end
