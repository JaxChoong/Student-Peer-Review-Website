require "rails_helper"

RSpec.describe PasswordMailer, type: :mailer do
  describe "reset_email" do
    let(:mail) { PasswordMailer.with(email: "to@example.org", token: "dummy_token").reset_email }

    it "renders the headers" do
      expect(mail.subject).to eq("Reset Your Password - Student Peer Review")
      expect(mail.to).to eq(["to@example.org"])
    end

    it "renders the body" do
      expect(mail.body.encoded).to match("Password Reset Request")
    end
  end

end
