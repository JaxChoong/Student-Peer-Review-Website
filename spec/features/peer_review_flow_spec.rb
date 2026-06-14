require 'rails_helper'

RSpec.feature "PeerReviewFlows", type: :feature do
  let!(:lecturer) { create(:user, role: 'lecturer') }
  let!(:student) { create(:user, role: 'student', password: 'password', password_confirmation: 'password') }
  let!(:teammate) { create(:user, name: 'John Doe', role: 'student') }
  
  let!(:course) { create(:course, lecturer: lecturer) }
  let!(:section) { create(:section, course: course, start_date: Date.today - 1, end_date: Date.today + 5) }
  let!(:group) { create(:group, course: course, section: section) }
  
  before do
    Capybara.current_driver = :rack_test

    create(:enrollment, user: student, course: course, section: section)
    create(:enrollment, user: teammate, course: course, section: section)
    create(:group_membership, user: student, group: group)
    create(:group_membership, user: teammate, group: group)

    layout = create(:question_layout, user: lecturer)
    @question = create(:question, question_layout: layout, question_text: "How was their communication?")
    course.update!(question_layout: layout)
  end

  scenario "Student logs in and submits a peer review" do
    visit login_path
    fill_in "email", with: student.email
    fill_in "password", with: "password"
    click_button "Log in"

    # Should be on dashboard, click 'Start Peer Review'
    expect(page).to have_content(course.course_code)
    click_link "Peer Review"

    expect(current_path).to eq(course_peer_reviews_start_path(course.id))
    expect(page).to have_content("Peer Evaluation")

    # The teammate name should be visible
    expect(page).to have_content(teammate.name)

    # Fill out the self-assessment
    # Textarea has name `answers[#{@question.id}]`
    fill_in "answers[#{@question.id}]", with: "I communicated very well with the team throughout the entire project timeline."

    # Fill out peer rating for teammate
    fill_in "reviews[#{teammate.id}][score]", with: "4"
    fill_in "reviews[#{teammate.id}][comment]", with: "John was a great leader. He really contributed a lot to the team effort and kept us on track."

    # Fill out peer rating for self
    fill_in "reviews[#{student.id}][score]", with: "5"
    fill_in "reviews[#{student.id}][comment]", with: "I worked very hard on this project and completed all of my assigned tasks on time."

    # Submit the form
    click_button "Normalize Ratings"
    # Wait for the button to be enabled before clicking
    expect(page).to have_button("Submit Final Review", disabled: false)
    click_button "Submit Final Review"

    expect(page).to have_content("Your peer review has been submitted successfully.")
    expect(current_path).to eq(dashboard_path)

    # Status should now be 'Submitted'
    expect(page).to have_content("Submitted")
  end
end
