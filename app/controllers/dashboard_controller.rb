class DashboardController < ApplicationController
  before_action :require_login

  def index
    if current_user.lecturer?
      @courses = current_user.courses.includes(:sections, :groups).order(created_at: :desc)
    else
      @courses = current_user.enrolled_courses.includes(:sections, :groups).order(created_at: :desc)
    end
  end
end
