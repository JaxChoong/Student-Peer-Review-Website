require 'rails_helper'

RSpec.describe Enrollment, type: :model do
  describe 'validations' do
    subject { build(:enrollment) } # Uniqueness validation requires a subject in the DB usually, but shoulda-matchers handles it if we don't have constraints, or we can just test the validation
    it { should validate_uniqueness_of(:user_id).scoped_to(:course_id, :section_id).with_message('is already enrolled in this section of the course') }
  end

  describe 'associations' do
    it { should belong_to(:course) }
    it { should belong_to(:section) }
    it { should belong_to(:user) }
  end
end
