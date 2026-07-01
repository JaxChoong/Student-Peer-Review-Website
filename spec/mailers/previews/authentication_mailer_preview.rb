# Preview all emails at http://localhost:3000/rails/mailers/authentication_mailer
class AuthenticationMailerPreview < ActionMailer::Preview

  # Preview this email at http://localhost:3000/rails/mailers/authentication_mailer/reset_email
  def reset_email
    AuthenticationMailer.with(email: "to@example.org", token: "dummy_token").reset_email
  end

  def new_account_email
    AuthenticationMailer.with(email: "to@example.org", token: "dummy_token").new_account_email
  end

  def temp_creds_email
    AuthenticationMailer.with(email: "to@example.org", token: "dummy_token", temp_password: "dummy_password").temp_creds_email
  end

end
