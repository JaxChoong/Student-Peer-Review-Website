require 'rails_helper'

RSpec.describe Section, type: :model do
  describe 'validations' do
    it { should validate_presence_of(:section_code) }
  end

  describe 'associations' do
    it { should belong_to(:course) }
    it { should have_many(:groups).dependent(:destroy) }
    it { should have_many(:enrollments).dependent(:destroy) }
    it { should have_many(:students).through(:enrollments).source(:user) }
    it { should have_many(:reviews).dependent(:destroy) }
    it { should have_many(:lecturer_ratings).dependent(:destroy) }
  end
end
