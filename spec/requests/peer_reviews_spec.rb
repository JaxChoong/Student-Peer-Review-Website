require 'rails_helper'

RSpec.describe "PeerReviews", type: :request do
  let!(:lecturer) { create(:user, role: 'lecturer') }
  let!(:student) { create(:user, role: 'student') }
  let!(:teammate) { create(:user, role: 'student') }
  
  let!(:course) { create(:course, lecturer: lecturer) }
  let!(:section) { create(:section, course: course, start_date: Date.today - 1, end_date: Date.today + 5) }
  let!(:group) { create(:group, course: course, section: section) }
  
  before do
    create(:enrollment, user: student, course: course, section: section)
    create(:enrollment, user: teammate, course: course, section: section)
    create(:group_membership, user: student, group: group)
    create(:group_membership, user: teammate, group: group)

    # Need a question layout for the course
    layout = create(:question_layout, user: lecturer)
    create(:question, question_layout: layout)
    course.update!(question_layout: layout)
  end

  describe "GET /peer_reviews/start/:course_id" do
    context "when not logged in" do
      it "redirects to login" do
        get course_peer_reviews_start_path(course.id)
        expect(response).to redirect_to(login_path)
      end
    end

    context "when logged in as student" do
      before do
        post login_path, params: { email: student.email, password: "password" }
      end

      it "renders the peer review form" do
        get course_peer_reviews_start_path(course.id)
        expect(response).to have_http_status(:success)
      end

      context "when deadline has passed" do
        before do
          section.update!(start_date: Date.today - 5, end_date: Date.today - 1)
        end

        it "redirects back to dashboard with error" do
          get course_peer_reviews_start_path(course.id)
          expect(response).to redirect_to(dashboard_path)
          expect(flash[:alert]).to include("Peer review")
        end
      end
    end
  end

  describe "POST /peer_reviews/:course_id" do
    before do
      post login_path, params: { email: student.email, password: "password" }
    end

    let(:valid_params) do
      {
        "reviews" => {
          teammate.id.to_s => { "score" => "3", "comment" => "Great team player!" }
        },
        "answers" => {
          course.question_layout.questions.first.id.to_s => "I did my best."
        }
      }
    end

    it "submits reviews and self assessments successfully" do
      expect {
        post course_peer_reviews_submit_path(course.id), params: valid_params
      }.to change(Review, :count).by(1).and change(SelfAssessment, :count).by(1)

      expect(response).to redirect_to(dashboard_path)
      expect(flash[:notice]).to eq("Your peer review has been submitted successfully.")
    end

    it "prevents duplicate submissions" do
      post course_peer_reviews_submit_path(course.id), params: valid_params
      
      expect {
        post course_peer_reviews_submit_path(course.id), params: valid_params
      }.not_to change(Review, :count)

      expect(response).to redirect_to(dashboard_path)
      expect(flash[:alert]).to include("already submitted")
    end
  end
end
