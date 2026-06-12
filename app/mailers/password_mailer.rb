class PasswordMailer < ApplicationMailer
  # Subject can be set in your I18n file at config/locales/en.yml
  # with the following lookup:
  #
  #   en.password_mailer.reset_email.subject
  #
  def reset_email
    @email = params[:email]
    @token = params[:token]
    @reset_url = reset_password_url(token: @token)

    mail to: @email, subject: "Reset Your Password - Student Peer Review"
  end
end
