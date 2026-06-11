require 'rails_helper'

RSpec.describe Course, type: :model do
  describe 'validations' do
    subject { build(:course) }
    it { should validate_presence_of(:course_code) }
    it { should validate_uniqueness_of(:course_code) }
    it { should validate_presence_of(:course_name) }
  end

  describe 'associations' do
    it { should belong_to(:lecturer).class_name('User') }
    it { should belong_to(:question_layout).optional }
    it { should belong_to(:introduction).optional }
    it { should have_many(:sections).dependent(:destroy) }
    it { should have_many(:groups).dependent(:destroy) }
    it { should have_many(:enrollments).dependent(:destroy) }
    it { should have_many(:students).through(:enrollments).source(:user) }
    it { should have_many(:reviews).dependent(:destroy) }
    it { should have_many(:self_assessments).dependent(:destroy) }
  end
end
