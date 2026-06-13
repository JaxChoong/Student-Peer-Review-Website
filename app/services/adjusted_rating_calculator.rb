class AdjustedRatingCalculator
  # AdjR = (rating / total_ratings) * 3 * num_students
  def self.call(rating:, total_ratings:, num_students:)
    return 0.0 if total_ratings.zero? || num_students.zero?
    
    ((rating.to_f / total_ratings) * 3.0 * num_students).round(2)
  end
end
