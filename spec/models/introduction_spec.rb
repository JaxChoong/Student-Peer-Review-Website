require 'rails_helper'

RSpec.describe Introduction, type: :model do
  describe 'validations' do
    it { should validate_presence_of(:content) }
  end

  describe 'associations' do
    it { should have_many(:courses).dependent(:nullify) }
  end
end
