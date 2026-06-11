require 'rails_helper'

RSpec.describe Question, type: :model do
  describe 'validations' do
    it { should validate_presence_of(:question_text) }
  end

  describe 'associations' do
    it { should belong_to(:question_layout) }
    it { should have_many(:self_assessments).dependent(:destroy) }
  end
end
