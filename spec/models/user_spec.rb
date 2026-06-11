require 'rails_helper'

RSpec.describe User, type: :model do
  describe 'validations' do
    subject { build(:user) }
    it { should validate_presence_of(:email) }
    it { should validate_uniqueness_of(:email) }
    it { should allow_value('test@example.com').for(:email) }
    it { should_not allow_value('invalid-email').for(:email) }
    it { should validate_presence_of(:name) }
    it { should validate_presence_of(:role) }
    it { should define_enum_for(:role).with_values(student: 'student', lecturer: 'lecturer').backed_by_column_of_type(:string) }
    it { should have_secure_password }
  end

  describe 'associations' do
    it { should have_many(:courses).with_foreign_key(:lecturer_id).dependent(:destroy) }
    it { should have_many(:enrollments).dependent(:destroy) }
    it { should have_many(:enrolled_courses).through(:enrollments).source(:course) }
    it { should have_many(:group_memberships).dependent(:destroy) }
    it { should have_many(:groups).through(:group_memberships) }
    it { should have_many(:reviews_given).class_name('Review').with_foreign_key(:reviewer_id).dependent(:destroy) }
    it { should have_many(:reviews_received).class_name('Review').with_foreign_key(:reviewee_id).dependent(:destroy) }
    it { should have_many(:self_assessments).dependent(:destroy) }
    it { should have_many(:lecturer_ratings_given).class_name('LecturerRating').with_foreign_key(:student_id).dependent(:destroy) }
    it { should have_many(:lecturer_ratings_received).class_name('LecturerRating').with_foreign_key(:lecturer_id).dependent(:destroy) }
  end
end
