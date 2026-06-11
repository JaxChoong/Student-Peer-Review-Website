class Introduction < ApplicationRecord
  has_many :courses, dependent: :nullify

  validates :content, presence: true
end
