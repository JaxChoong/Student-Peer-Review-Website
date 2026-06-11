require 'rails_helper'

RSpec.describe PasswordReset, type: :model do
  describe 'validations' do
    it { should validate_presence_of(:email) }
    it { should allow_value('test@example.com').for(:email) }
    it { should_not allow_value('invalid-email').for(:email) }
    
    # We can't easily test uniqueness of secure token with shoulda-matchers without a subject usually, but we can verify presence
    it { should validate_presence_of(:token) }
  end

  describe '#expired?' do
    it 'returns true if created_at is older than 24 hours' do
      reset = PasswordReset.new(created_at: 25.hours.ago)
      expect(reset.expired?).to be true
    end

    it 'returns false if created_at is within 24 hours' do
      reset = PasswordReset.new(created_at: 23.hours.ago)
      expect(reset.expired?).to be false
    end
  end
end
