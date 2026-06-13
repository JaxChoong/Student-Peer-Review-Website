require 'rails_helper'

RSpec.feature "AuthenticationFlows", type: :feature do
  before do
    # Ensure rack_test is used for features (no Chrome needed)
    Capybara.current_driver = :rack_test
  end

  scenario "User registers a new account and logs in" do
    visit root_path
    
    # Wait for the page to load and find the Get Started button (or go straight to /register)
    visit register_path

    fill_in "user_name", with: "Test Student"
    fill_in "user_email", with: "student_feature@mmu.edu.my"
    fill_in "user_student_number", with: "123456789"
    fill_in "user_password", with: "password123"
    fill_in "user_password_confirmation", with: "password123"

    click_button "Register"

    expect(page).to have_content("Account created successfully")
    expect(current_path).to eq(dashboard_path)

    # Now let's test logout
    click_button "Log Out", match: :first
    expect(page).to have_content("Logged out successfully")
    expect(current_path).to eq(root_path)

    # Now let's test login
    visit login_path
    fill_in "email", with: "student_feature@mmu.edu.my"
    fill_in "password", with: "password123"
    click_button "Log in"

    expect(page).to have_content("Logged in successfully")
    expect(current_path).to eq(dashboard_path)
  end

  scenario "User tries to log in with invalid credentials" do
    visit login_path
    fill_in "email", with: "invalid@example.com"
    fill_in "password", with: "wrong_password"
    click_button "Log in"

    expect(page).to have_content("Invalid email or password")
    expect(current_path).to eq(login_path)
  end
end
