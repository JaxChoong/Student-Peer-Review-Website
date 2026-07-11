module EmailNormalizable
  extend ActiveSupport::Concern

  included do
    def email=(value)
      super(value&.downcase)
    end
  end
end
