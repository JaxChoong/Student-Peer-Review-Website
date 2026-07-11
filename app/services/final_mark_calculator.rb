class FinalMarkCalculator
  # Returns a hash with detailed breakdown:
  # {
  #   am: assignment_mark (0-100),
  #   apr: average_peer_rating_with_penalty (0-3),
  #   raw_apr: average_peer_rating_without_penalty (0-3),
  #   le: lecturer_evaluation (0-3),
  #   penalty: true/false (did not submit peer review),
  #   submitted_review: true/false,
  #   final_mark: final_calculated_score (0-100)
  # }
  def self.call(student:, group:, rubric_max: nil)
    course = group.course

    submitted_review = Review.exists?(reviewer: student, group: group)
    reviews_received = Review.where(reviewee: student, group: group)
    raw_apr = reviews_received.any? ? (reviews_received.sum(:score) / reviews_received.count).to_f : 0.0

    penalty_multiplier = 1.0
    if !submitted_review && course.apply_penalty
      penalty_percentage = course.penalty_percentage || 100
      penalty_multiplier = (100 - penalty_percentage) / 100.0
      penalty_multiplier = [penalty_multiplier, 0.0].max
    end

    penalized_apr = raw_apr * penalty_multiplier

    if course.raw_peer_ratings?
      return {
        am: 0.0,
        raw_apr: raw_apr.round(2),
        apr: penalized_apr.round(2),
        le: 0.0,
        penalty: !submitted_review,
        submitted_review: submitted_review,
        final_mark: penalized_apr.round(2)
      }
    end

    group_mark = group.final_group_mark&.mark || 0.0

    lecturer_rating = LecturerRating.find_by(student: student, section: group.section)
    le = lecturer_rating ? lecturer_rating.rating.to_f : penalized_apr

    denominator = course.rubric_scoring? ? (rubric_max || 3.0).to_f : 3.0
    denominator = 3.0 if denominator.zero?

    apr_ratio = penalized_apr / denominator
    le_ratio = le / denominator
    am_float = group_mark.to_f

    final_mark = (0.5 * am_float) + (0.25 * am_float * apr_ratio) + (0.25 * am_float * le_ratio)

    {
      am: am_float.round(2),
      raw_apr: raw_apr.round(2),
      apr: penalized_apr.round(2),
      le: le.round(2),
      penalty: !submitted_review,
      submitted_review: submitted_review,
      final_mark: final_mark.round(2)
    }
  end
end
