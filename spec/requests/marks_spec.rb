require 'rails_helper'

RSpec.describe "Marks", type: :request do
  let!(:lecturer) { create(:user, role: 'lecturer') }
  let!(:course) { create(:course, lecturer: lecturer) }
  let!(:section) { create(:section, course: course) }
  let!(:group) { create(:group, course: course, section: section) }
  let!(:student) { create(:user, role: 'student') }
  
  before do
    create(:enrollment, user: student, course: course, section: section)
    create(:group_membership, user: student, group: group)
  end

  describe "GET /marks/:course_id" do
    context "when logged in as lecturer" do
      before do
        post login_path, params: { email: lecturer.email, password: "password" }
      end

      it "renders the marks dashboard" do
        get course_marks_path(course.id)
        expect(response).to have_http_status(:success)
      end
    end

    context "when logged in as student" do
      before do
        post login_path, params: { email: student.email, password: "password" }
      end

      it "redirects away (unauthorized)" do
        get course_marks_path(course.id)
        expect(response).to redirect_to(dashboard_path)
      end
    end
  end

  describe "POST /marks/:course_id/import" do
    before do
      post login_path, params: { email: lecturer.email, password: "password" }
    end

    let(:temp_dir) { Dir.mktmpdir }
    let(:csv_path) do
      path = File.join(temp_dir, 'marks.csv')
      File.write(path, "Student Email,Group Mark,Lecturer Rating\n#{student.email},85.5,2.8")
      path
    end

    after do
      FileUtils.remove_entry temp_dir
    end

    it "imports the marks and lecturer ratings successfully" do
      expect {
        post import_course_marks_path(course.id), params: { 
          file: fixture_file_upload(csv_path, 'text/csv') 
        }
      }.to change(FinalGroupMark, :count).by(1).and change(LecturerRating, :count).by(1)

      expect(response).to redirect_to(course_marks_path(course.id))
      expect(flash[:notice]).to match(/Marks imported successfully/)

      expect(group.final_group_mark.mark).to eq(85.5)
      expect(LecturerRating.find_by(student: student).rating).to eq(2.8)
    end
  end

  describe "GET /marks/:course_id/export" do
    before do
      post login_path, params: { email: lecturer.email, password: "password" }
      create(:final_group_mark, group: group, mark: 90.0)
    end

    it "downloads the final marks CSV" do
      get export_final_course_marks_path(course.id, format: :csv)
      expect(response).to have_http_status(:success)
      expect(response.headers['Content-Type']).to include('text/csv')
      expect(response.body).to include(student.name)
    end
  end
end
