source "https://rubygems.org"

gem "rails", "~> 8.1.3"

# Asset pipeline
gem "propshaft"
gem "importmap-rails"
gem "stimulus-rails"

# Database
gem "pg", "~> 1.1"

# Web server
gem "puma", ">= 5.0"

# Password hashing
gem "bcrypt", "~> 3.1.7"

# .env file loading (dev + test)
gem "dotenv-rails"

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
  gem "rubocop-rails-omakase", require: false
  gem "web-console"
end

group :test do
  gem "capybara"
  gem "selenium-webdriver"
  gem "webdrivers"
  gem "database_cleaner-active_record"
end

gem "ffi", "~> 1.17"

gem "tailwindcss-rails", "~> 4.4"

gem "brakeman", "~> 8.0", groups: [:development, :test]
gem "bundler-audit", "~> 0.9.3", groups: [:development, :test]

gem "csv", "~> 3.3"
