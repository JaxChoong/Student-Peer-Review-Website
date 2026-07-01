class AuthenticationMailer < ApplicationMailer
  def reset_email
    @email = params[:email]
    @token = params[:token]
    @reset_url = reset_password_url(token: @token)

    mail to: @email, subject: "Reset Your Password - Student Peer Review"
  end

  def new_account_email
    @email = params[:email]
    @token = params[:token]
    @reset_url = reset_password_url(token: @token)

    mail to: @email, subject: "Welcome to Student Peer Review - Setup Your Account"
  end

  def temp_creds_email
    @email = params[:email]
    @token = params[:token]
    @temp_password = params[:temp_password]
    @reset_url = reset_password_url(token: @token)

    mail to: @email, subject: "Your Temporary Credentials - Student Peer Review"
  end
end
