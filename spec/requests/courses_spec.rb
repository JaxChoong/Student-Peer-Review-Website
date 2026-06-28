require 'rails_helper'

RSpec.describe "Courses", type: :request do
  let!(:lecturer) { create(:user, role: 'lecturer') }
  let!(:student) { create(:user, role: 'student') }
  
  describe "GET /dashboard" do
    context "when not logged in" do
      it "redirects to login" do
        get dashboard_path
        expect(response).to redirect_to(login_path)
      end
    end

    context "when logged in as lecturer" do
      before do
        post login_path, params: { email: lecturer.email, password: "password" }
      end

      it "renders the dashboard successfully" do
        get dashboard_path
        expect(response).to have_http_status(:success)
      end
    end

    context "when logged in as student" do
      before do
        post login_path, params: { email: student.email, password: "password" }
      end

      it "renders the dashboard successfully" do
        get dashboard_path
        expect(response).to have_http_status(:success)
      end
    end
  end

  describe "POST /courses" do
    before do
      post login_path, params: { email: lecturer.email, password: "password" }
    end

    context "with valid parameters" do
      it "creates a course and redirects to course groups" do
        expect {
          post courses_path, params: { 
            course_code: "CS101",
            course_name: "Test Course",
            start_date: "2026-06-14",
            end_date: "2026-06-21"
          }
        }.to change(Course, :count).by(1)

        expect(response).to redirect_to(course_groups_path(Course.last))
        expect(flash[:notice]).to match(/Course created successfully/)
      end
    end

    context "with invalid parameters" do
      it "redirects back with validation error" do
        post courses_path, params: {}
        expect(response).to redirect_to(new_course_path)
        expect(flash[:alert]).to match(/Course code can't be blank/)
      end
    end
  end

  describe "PATCH /courses/:id/update_settings" do
    let!(:course) { create(:course, lecturer: lecturer, start_date: 1.day.from_now, end_date: 5.days.from_now) }

    before do
      post login_path, params: { email: lecturer.email, password: "password" }
    end

    context "when review has not started" do
      it "updates the review mode successfully" do
        expect(course.review_mode).to eq("raw_peer_ratings")
        patch update_settings_course_path(course), params: { review_mode: 1 } # normalised_peer_ratings
        expect(response).to redirect_to(course_groups_path(course))
        expect(flash[:notice]).to eq("Course settings updated successfully.")
        expect(course.reload.review_mode).to eq("normalised_peer_ratings")
      end
    end

    context "when review has started" do
      before do
        course.update!(start_date: Date.today)
      end

      it "does not update the review mode and returns an alert" do
        expect(course.review_started?).to be true
        patch update_settings_course_path(course), params: { review_mode: 1 } # normalised_peer_ratings
        expect(response).to redirect_to(course_groups_path(course))
        expect(flash[:alert]).to eq("Settings are locked and cannot be changed after the review starts.")
        expect(course.reload.review_mode).to eq("raw_peer_ratings")
      end
    end
  end
end
