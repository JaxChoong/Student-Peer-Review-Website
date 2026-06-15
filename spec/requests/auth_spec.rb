require 'rails_helper'

RSpec.describe "Auths", type: :request do
  describe "GET /login" do
    it "returns http success" do
      get login_path
      expect(response).to have_http_status(:success)
    end
  end

  describe "POST /login" do
    let!(:user) { create(:user, email: "test@mmu.edu.my", password: "password", password_confirmation: "password") }

    it "logs in the user and redirects to dashboard" do
      post login_path, params: { email: user.email, password: "password" }
      expect(session[:user_id]).to eq(user.id)
      expect(response).to redirect_to(dashboard_path)
    end

    it "fails with invalid password format" do
      post login_path, params: { email: user.email, password: "wrong" }
      expect(session[:user_id]).to be_nil
      expect(response.body).to include("Invalid password format")
    end

    it "fails with incorrect password" do
      post login_path, params: { email: user.email, password: "wrongpassword" }
      expect(session[:user_id]).to be_nil
      expect(response.body).to include("Incorrect password")
    end
  end

  describe "POST /register" do
    it "creates a new user and redirects" do
      expect {
        post register_path, params: { 
          user: { 
            name: "New Student", 
            email: "new@student.mmu.edu.my", 
            student_number: "1191100000",
            password: "password", 
            password_confirmation: "password" 
          } 
        }
      }.to change(User, :count).by(1)

      user = User.last
      expect(user.role).to eq('student')
      expect(session[:user_id]).to eq(user.id)
      expect(response).to redirect_to(dashboard_path)
    end

    it "assigns lecturer role if email is @mmu.edu.my" do
      post register_path, params: { 
        user: { 
          name: "Lecturer", 
          email: "lecturer@mmu.edu.my", 
          password: "password", 
          password_confirmation: "password" 
        } 
      }
      user = User.last
      expect(user.role).to eq('lecturer')
    end
  end

  describe "DELETE /logout" do
    it "clears the session" do
      # Simulate login first
      post login_path, params: { email: create(:user).email, password: "password" }
      expect(session[:user_id]).not_to be_nil

      delete logout_path
      expect(session[:user_id]).to be_nil
      expect(response).to redirect_to(root_path)
    end
  end
end
