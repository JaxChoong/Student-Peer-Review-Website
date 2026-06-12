require "rails_helper"

RSpec.describe PasswordMailer, type: :mailer do
  describe "reset_email" do
    let(:mail) { PasswordMailer.reset_email }

    it "renders the headers" do
      expect(mail.subject).to eq("Reset email")
      expect(mail.to).to eq(["to@example.org"])
      expect(mail.from).to eq(["from@example.com"])
    end

    it "renders the body" do
      expect(mail.body.encoded).to match("Hi")
    end
  end

end
