class FinalMarkCalculator
  # Returns a hash with detailed breakdown:
  # {
  #   am: assignment_mark (0-100),
  #   apr: average_peer_rating (0-3),
  #   le: lecturer_evaluation (0-3),
  #   penalty: true/false (did not submit peer review),
  #   final_mark: final_calculated_score (0-100)
  # }
  def self.call(student:, group:, rubric_max: nil)
    course = group.course

    submitted_review = Review.exists?(reviewer: student, group: group)
    reviews_received = Review.where(reviewee: student, group: group)
    apr = reviews_received.any? ? (reviews_received.sum(:score) / reviews_received.count).to_f : 0.0

    if course.peer_ratings_only?
      return {
        am: 0.0,
        apr: submitted_review ? apr.round(2) : 0.0,
        le: 0.0,
        penalty: !submitted_review,
        final_mark: submitted_review ? apr.round(2) : 0.0
      }
    end

    if !submitted_review
      return { am: 0.0, apr: 0.0, le: 0.0, penalty: true, final_mark: 0.0 }
    end

    group_mark = group.final_group_mark&.mark || 0.0

    lecturer_rating = LecturerRating.find_by(student: student, section: group.section)
    le = lecturer_rating ? lecturer_rating.rating.to_f : apr

    denominator = course.rubric_scoring? ? (rubric_max || 3.0).to_f : 3.0
    denominator = 3.0 if denominator.zero?

    apr_ratio = apr / denominator
    le_ratio = le / denominator
    am_float = group_mark.to_f

    final_mark = (0.5 * am_float) + (0.25 * am_float * apr_ratio) + (0.25 * am_float * le_ratio)

    {
      am: am_float.round(2),
      apr: apr.round(2),
      le: le.round(2),
      penalty: false,
      final_mark: final_mark.round(2)
    }
  end
end
