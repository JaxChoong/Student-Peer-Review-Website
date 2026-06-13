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

    context "with valid CSV upload" do
      let(:temp_dir) { Dir.mktmpdir }
      let(:csv_path) do
        path = File.join(temp_dir, 'students.csv')
        File.write(path, "email,name,section,group\ntest@student.mmu.edu.my,Test Student,TC1,G1")
        path
      end

      after do
        FileUtils.remove_entry temp_dir
      end

      it "creates a course and redirects to dashboard" do
        expect {
          post courses_path, params: { 
            file: fixture_file_upload(csv_path, 'text/csv') 
          }
        }.to change(Course, :count).by(1)

        expect(response).to redirect_to(dashboard_path)
        expect(flash[:notice]).to match(/Course created successfully/)
      end
    end

    context "with no file" do
      it "redirects back with error" do
        post courses_path, params: {}
        expect(response).to redirect_to(new_course_path)
        expect(flash[:alert]).to eq("Please upload a CSV file.")
      end
    end
  end
end
