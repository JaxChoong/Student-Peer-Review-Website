require 'rails_helper'

RSpec.describe LecturerRating, type: :model do
  describe 'validations' do
    subject { build(:lecturer_rating) }
    it { should validate_numericality_of(:rating).is_greater_than_or_equal_to(0).is_less_than_or_equal_to(3).allow_nil }
    it { should validate_uniqueness_of(:lecturer_id).scoped_to(:student_id, :section_id) }
  end

  describe 'associations' do
    it { should belong_to(:lecturer).class_name('User') }
    it { should belong_to(:student).class_name('User') }
    it { should belong_to(:section) }
  end
end
