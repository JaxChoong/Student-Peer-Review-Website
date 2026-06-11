require 'rails_helper'

RSpec.describe SelfAssessment, type: :model do
  describe 'validations' do
    subject { build(:self_assessment) }
    it { should validate_uniqueness_of(:user_id).scoped_to(:course_id, :question_id).with_message('has already submitted an assessment for this question') }
    it { should validate_presence_of(:question_text) }
    it { should validate_presence_of(:answer) }
  end

  describe 'associations' do
    it { should belong_to(:course) }
    it { should belong_to(:question) }
    it { should belong_to(:user) }
  end
end
