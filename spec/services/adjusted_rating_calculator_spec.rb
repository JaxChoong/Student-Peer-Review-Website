require 'rails_helper'

RSpec.describe AdjustedRatingCalculator do
  describe '.call' do
    it 'calculates the adjusted rating correctly' do
      # AdjR = (rating / total_ratings) * 3 * num_students
      # E.g. rating: 8, total_ratings: 20, num_students: 4
      # AdjR = (8 / 20) * 3 * 4 = 0.4 * 12 = 4.8
      result = AdjustedRatingCalculator.call(rating: 8, total_ratings: 20, num_students: 4)
      expect(result).to eq(4.8)
    end

    it 'returns 0.0 if total_ratings is zero (student teammates did not give ratings)' do
      result = AdjustedRatingCalculator.call(rating: 0, total_ratings: 0, num_students: 4)
      expect(result).to eq(0.0)
    end

    it 'returns 0.0 if num_students is zero' do
      result = AdjustedRatingCalculator.call(rating: 10, total_ratings: 10, num_students: 0)
      expect(result).to eq(0.0)
    end

    it 'handles scenarios where a teammate drops out and missing ratings are safely ignored in the math' do
      # Original group of 4: Expected total rating = 4 * 3 = 12.
      # If one student drops out, the num_students might be evaluated as 3 for the remaining logic,
      # and total_ratings will be out of 9 instead of 12.
      result = AdjustedRatingCalculator.call(rating: 6, total_ratings: 9, num_students: 3)
      expect(result).to eq(6.0) # (6/9) * 3 * 3 = 6.0
    end
  end
end
