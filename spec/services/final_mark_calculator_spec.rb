require 'rails_helper'

RSpec.describe FinalMarkCalculator do
  let(:course) { create(:course) }
  let(:section) { create(:section, course: course) }
  let(:group) { create(:group, course: course, section: section) }
  let(:student) { create(:user, role: 'student') }
  let(:lecturer) { create(:user, role: 'lecturer') }
  let!(:enrollment) { create(:enrollment, user: student, course: course, section: section) }
  let!(:membership) { create(:group_membership, user: student, group: group) }
  
  before do
    create(:final_group_mark, group: group, mark: 80.0)
  end

  describe '.call' do
    context 'when student does not submit their peer review' do
      it 'applies a penalty and returns 0.0 for everything' do
        # No review created for student -> group
        result = FinalMarkCalculator.call(student: student, group: group)

        expect(result[:penalty]).to be true
        expect(result[:am]).to eq(0.0)
        expect(result[:apr]).to eq(0.0)
        expect(result[:le]).to eq(0.0)
        expect(result[:final_mark]).to eq(0.0)
      end
    end

    context 'when student submits peer review' do
      before do
        # Student submits a review
        create(:review, reviewer: student, reviewee: create(:user), group: group, score: 2.0)
      end

      context 'with standard inputs' do
        before do
          # Peers give this student an average of 2.5
          create(:review, reviewer: create(:user), reviewee: student, group: group, score: 3.0)
          create(:review, reviewer: create(:user), reviewee: student, group: group, score: 2.0)
          # Lecturer gives 2.8
          create(:lecturer_rating, student: student, section: section, lecturer: lecturer, rating: 2.8)
        end

        it 'calculates the final mark correctly' do
          result = FinalMarkCalculator.call(student: student, group: group)

          expect(result[:penalty]).to be false
          expect(result[:am]).to eq(80.0)
          expect(result[:apr]).to eq(2.5)
          expect(result[:le]).to eq(2.8)

          # Final = (0.5 * 80) + (0.25 * 80 * (2.5 / 3.0)) + (0.25 * 80 * (2.8 / 3.0))
          # = 40 + 16.666 + 18.666 = 75.33
          expect(result[:final_mark]).to be_within(0.05).of(75.33)
        end
      end

      context 'when lecturer rating is not given' do
        before do
          # Peers give this student an average of 2.0
          create(:review, reviewer: create(:user), reviewee: student, group: group, score: 2.0)
          # No lecturer rating created
        end

        it 'defaults the LE to the APR' do
          result = FinalMarkCalculator.call(student: student, group: group)

          expect(result[:le]).to eq(2.0)
          expect(result[:apr]).to eq(2.0)
          
          # Final = (0.5 * 80) + (0.25 * 80 * (2.0 / 3.0)) + (0.25 * 80 * (2.0 / 3.0))
          # = 40 + 13.333 + 13.333 = 66.67
          expect(result[:final_mark]).to be_within(0.05).of(66.67)
        end
      end

      context 'when teammates do not give ratings' do
        # E.g. no peers submit reviews for this student
        it 'returns APR as 0.0 but continues calculation' do
          result = FinalMarkCalculator.call(student: student, group: group)

          expect(result[:apr]).to eq(0.0)
          expect(result[:le]).to eq(0.0) # Defaults to APR since missing LE

          # Final = (0.5 * 80) + 0 + 0 = 40.0
          expect(result[:final_mark]).to eq(40.0)
        end
      end
    end
  end
end
