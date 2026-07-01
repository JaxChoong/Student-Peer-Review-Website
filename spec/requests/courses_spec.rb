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

  # ── Legacy individual endpoint ────────────────────────────────────────────
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
        section = create(:section, course: course)
        group = create(:group, course: course, section: section)
        reviewer = create(:user, role: 'student')
        reviewee = create(:user, role: 'student')
        create(:review, course: course, section: section, group: group, reviewer: reviewer, reviewee: reviewee)
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

  # ── Consolidated update_all_settings endpoint ─────────────────────────────
  describe "PATCH /courses/:id/update_all_settings" do
    let!(:course) { create(:course, lecturer: lecturer, start_date: 1.day.from_now, end_date: 5.days.from_now) }

    before do
      post login_path, params: { email: lecturer.email, password: "password" }
    end

    context "when review has not started" do
      it "updates review mode successfully" do
        patch update_all_settings_course_path(course), params: {
          review_mode: 1,
          scoring_scheme: 0,
          start_date: 2.days.from_now.to_date.to_s,
          end_date: 10.days.from_now.to_date.to_s
        }
        expect(response).to redirect_to(course_groups_path(course))
        expect(flash[:notice]).to eq("Course settings updated successfully.")
        expect(course.reload.review_mode).to eq("normalised_peer_ratings")
      end

      it "updates the course introduction" do
        patch update_all_settings_course_path(course), params: {
          content: "# Welcome\n\nThis is the intro.",
          start_date: 2.days.from_now.to_date.to_s,
          end_date: 10.days.from_now.to_date.to_s
        }
        expect(response).to redirect_to(course_groups_path(course))
        expect(course.reload.introduction.content).to eq("# Welcome\n\nThis is the intro.")
      end

      it "updates the global review dates and cascades to sections" do
        section = create(:section, course: course)
        new_start = 3.days.from_now.to_date.to_s
        new_end   = 15.days.from_now.to_date.to_s

        patch update_all_settings_course_path(course), params: {
          start_date: new_start,
          end_date:   new_end
        }

        expect(response).to redirect_to(course_groups_path(course))
        course.reload
        expect(course.start_date.to_s).to eq(new_start)
        expect(course.end_date.to_s).to eq(new_end)
        expect(section.reload.start_date.to_s).to eq(new_start)
        expect(section.reload.end_date.to_s).to eq(new_end)
      end

      it "rejects when end_date is not after start_date" do
        patch update_all_settings_course_path(course), params: {
          start_date: 5.days.from_now.to_date.to_s,
          end_date:   2.days.from_now.to_date.to_s
        }
        expect(response).to redirect_to(course_groups_path(course))
        expect(flash[:alert]).to eq("Close date must be after the open date.")
        # Dates must remain unchanged
        expect(course.reload.end_date).to eq(5.days.from_now.to_date)
      end

      it "rejects when end_date equals start_date" do
        same_date = 3.days.from_now.to_date.to_s
        patch update_all_settings_course_path(course), params: {
          start_date: same_date,
          end_date:   same_date
        }
        expect(response).to redirect_to(course_groups_path(course))
        expect(flash[:alert]).to eq("Close date must be after the open date.")
      end

      it "enforces backend: rubric scheme not allowed in normalised mode" do
        patch update_all_settings_course_path(course), params: {
          review_mode: 1,    # normalised
          scoring_scheme: 1  # rubric — incompatible
        }
        course.reload
        expect(course.review_mode).to eq("normalised_peer_ratings")
        expect(course.scoring_scheme).to eq("numeric") # fallback to numeric (0)
      end

      it "enforces backend: point pool not allowed in raw mode" do
        patch update_all_settings_course_path(course), params: {
          review_mode: 0,    # raw
          scoring_scheme: 2  # point pool — incompatible
        }
        course.reload
        expect(course.review_mode).to eq("raw_peer_ratings")
        expect(course.scoring_scheme).to eq("numeric") # fallback
      end
    end

    context "when review has started (settings locked)" do
      before do
        course.update!(start_date: Date.today)
        section = create(:section, course: course)
        group = create(:group, course: course, section: section)
        reviewer = create(:user, role: 'student')
        reviewee = create(:user, role: 'student')
        create(:review, course: course, section: section, group: group, reviewer: reviewer, reviewee: reviewee)
      end

      it "does not update the review mode but still redirects with notice" do
        expect(course.review_started?).to be true
        patch update_all_settings_course_path(course), params: { review_mode: 1 }
        expect(response).to redirect_to(course_groups_path(course))
        # Settings are skipped; no error for the locked section
        expect(course.reload.review_mode).to eq("raw_peer_ratings")
      end

      it "still updates the introduction when locked" do
        patch update_all_settings_course_path(course), params: {
          content: "Updated intro after lock."
        }
        expect(response).to redirect_to(course_groups_path(course))
        expect(course.reload.introduction.content).to eq("Updated intro after lock.")
      end
    end

    context "when accessed by another lecturer" do
      let!(:other_lecturer) { create(:user, role: 'lecturer') }
      let!(:other_course) { create(:course, lecturer: other_lecturer, start_date: 1.day.from_now, end_date: 5.days.from_now) }

      it "cannot update another lecturer's course — redirects to dashboard with alert" do
        # Log out the current session (lecturer was logged in by the before block),
        # then log in as other_lecturer. The auth controller requires logout before login.
        delete logout_path
        post login_path, params: { email: other_lecturer.email, password: "password" }
        patch update_all_settings_course_path(course), params: { review_mode: 1 }
        expect(response).to redirect_to(dashboard_path)
        expect(flash[:alert]).to eq("Course not found.")
      end
    end
  end
end
