class BatchSendCredentialsJob < ApplicationJob
  queue_as :default

  def perform(new_users)
    new_users.each do |user_data|
      email, _name, temp_password = user_data
      # We use request_reset with the mailer_method :temp_creds_email and pass the temp_password
      PasswordResetService.request_reset(email, mailer_method: :temp_creds_email, temp_password: temp_password)
    end
  end
end
