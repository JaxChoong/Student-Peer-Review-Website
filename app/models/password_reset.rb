class PasswordReset < ApplicationRecord
  has_secure_token :token

  validates :email, presence: true, format: { with: URI::MailTo::EMAIL_REGEXP }
  validates :token, presence: true, uniqueness: true

  def expired?
    created_at < 24.hours.ago
  end
end
