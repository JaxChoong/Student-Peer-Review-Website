require 'rails_helper'

RSpec.describe QuestionLayout, type: :model do
  describe 'validations' do
    it { should validate_presence_of(:layout_name) }
  end

  describe 'associations' do
    it { should belong_to(:user).optional }
    it { should have_many(:questions).dependent(:destroy) }
    it { should have_many(:courses).dependent(:nullify) }
  end
end
