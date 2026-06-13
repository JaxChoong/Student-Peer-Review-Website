class ReviewDateChecker
  # Returns [:open | :not_yet | :closed | :unset, message_string]
  def self.call(section)
    return [:unset, "No review dates set."] unless section.start_date && section.end_date
    
    today = Date.today
    
    if today.between?(section.start_date, section.end_date)
      [:open, "Peer review is open from #{section.start_date.strftime('%d %b %Y')} to #{section.end_date.strftime('%d %b %Y')}."]
    elsif today < section.start_date
      [:not_yet, "Peer review opens on #{section.start_date.strftime('%d %b %Y')}."]
    else
      [:closed, "Peer review closed on #{section.end_date.strftime('%d %b %Y')}."]
    end
  end
end
