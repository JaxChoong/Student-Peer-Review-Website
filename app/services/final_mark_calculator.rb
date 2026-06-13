class FinalMarkCalculator
  # Returns a hash with detailed breakdown:
  # {
  #   am: assignment_mark (0-100),
  #   apr: average_peer_rating (0-3),
  #   le: lecturer_evaluation (0-3),
  #   penalty: true/false (did not submit peer review),
  #   final_mark: final_calculated_score (0-100)
  # }
  def self.call(student:, group:)
    course = group.course

    # 1. Did they submit their peer review?
    # If they did not submit any reviews for this group, they get an automatic 0 for everything.
    submitted_review = Review.exists?(reviewer: student, group: group)
    if !submitted_review
      return { am: 0.0, apr: 0.0, le: 0.0, penalty: true, final_mark: 0.0 }
    end

    # 2. Assignment Mark (AM)
    # This is the overall mark given to the group by the lecturer
    group_mark = group.final_group_mark&.mark || 0.0

    # 3. Average Peer Rating (APR)
    # The average of the adjusted ratings (AdjR) given TO this student by peers
    reviews_received = Review.where(reviewee: student, group: group)
    apr = if reviews_received.any?
      (reviews_received.sum(:score) / reviews_received.count).to_f
    else
      0.0
    end

    # 4. Lecturer Evaluation (LE)
    # The lecturer rating given to this student. If not provided, it defaults to their APR.
    lecturer_rating = LecturerRating.find_by(student: student, section: group.section)
    le = lecturer_rating ? lecturer_rating.rating.to_f : apr

    # 5. Calculate Final Mark
    # Formula: Final = (0.5 * AM) + (0.25 * AM * (APR / 3.0)) + (0.25 * AM * (LE / 3.0))
    am_float = group_mark.to_f
    
    # Avoid division by zero issues, max out at 3.0 theoretically
    apr_ratio = apr / 3.0
    le_ratio = le / 3.0

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
