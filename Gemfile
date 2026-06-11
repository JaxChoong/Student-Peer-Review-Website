source "https://rubygems.org"

gem "rails", "~> 8.1.3"

# Asset pipeline
gem "propshaft"

# Database
gem "pg", "~> 1.1"

# Web server
gem "puma", ">= 5.0"

# Password hashing
gem "bcrypt", "~> 3.1.7"

# .env file loading (dev + test)
gem "dotenv-rails", groups: [:development, :test]

# Boot time caching
gem "bootsnap", require: false

# Windows timezone data
gem "tzinfo-data", platforms: %i[ windows jruby ]

group :development, :test do
  gem "rspec-rails"
  gem "factory_bot_rails"
  gem "faker"
  gem "shoulda-matchers"
  gem "debug", platforms: %i[ mri windows ], require: "debug/prelude"
end

group :development do
  gem "web-console"
end

group :test do
  gem "capybara"
  gem "selenium-webdriver"
  gem "webdrivers"
  gem "database_cleaner-active_record"
end
