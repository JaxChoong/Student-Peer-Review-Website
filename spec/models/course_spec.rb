require 'rails_helper'

RSpec.describe Course, type: :model do
  describe 'validations' do
    subject { build(:course) }
    it { should validate_presence_of(:course_code) }
    it { should validate_uniqueness_of(:course_code) }
    it { should validate_presence_of(:course_name) }
    it { should validate_presence_of(:review_mode) }
  end

  describe 'review_mode enum' do
    it 'defaults to peer_ratings_only' do
      course = Course.new
      expect(course.review_mode).to eq('peer_ratings_only')
    end

    it 'defines modes correctly' do
      expect(Course.review_modes.keys).to eq(['peer_ratings_only', 'hybrid'])
    end
  end

  describe '#review_started?' do
    let(:course) { create(:course, start_date: 1.day.from_now, end_date: 5.days.from_now) }

    context 'when review start date is in the future and there are no submissions' do
      it 'returns false' do
        expect(course.review_started?).to be false
      end
    end

    context 'when review start date has been reached' do
      it 'returns true' do
        course.update!(start_date: Date.today)
        expect(course.review_started?).to be true
      end
    end

    context 'when start date has not been reached but a review exists' do
      it 'returns true' do
        reviewer = create(:user, role: 'student')
        reviewee = create(:user, role: 'student')
        section = create(:section, course: course)
        group = create(:group, course: course, section: section)
        create(:review, course: course, section: section, group: group, reviewer: reviewer, reviewee: reviewee)
        
        expect(course.review_started?).to be true
      end
    end

    context 'when start date has not been reached but a self assessment exists' do
      it 'returns true' do
        student = create(:user, role: 'student')
        layout = create(:question_layout)
        question = create(:question, question_layout: layout)
        course.update!(question_layout: layout)
        create(:self_assessment, course: course, question: question, user: student)

        expect(course.review_started?).to be true
      end
    end
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
