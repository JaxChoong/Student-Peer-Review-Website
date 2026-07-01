class PasswordResetService
  # Create token, persist, send email
  def self.request_reset(email, mailer_method: :reset_email, **kwargs)
    token = SecureRandom.urlsafe_base64(32)
    
    # Store token in database
    PasswordReset.create!(email: email, token: token)
    
    # Send email
    mailer_params = { email: email, token: token }.merge(kwargs)
    AuthenticationMailer.with(mailer_params).send(mailer_method).deliver_later
  end

  # Validate token age (< 24h) and return associated email
  def self.validate_token(token)
    reset = PasswordReset.find_by(token: token)
    
    if reset && reset.created_at > 24.hours.ago
      reset.email
    else
      nil
    end
  end
end
