class ApplicationController < ActionController::Base
  # Only allow modern browsers supporting webp images, web push, badges, import maps, CSS nesting, and CSS :has.
  allow_browser versions: :modern

  helper_method :current_user

  def current_user
    @current_user ||= User.find_by(id: session[:user_id])
  end

  def require_login
    redirect_to login_path, alert: "Please log in." unless current_user
  end

  def require_logout
    redirect_to dashboard_path if current_user
  end

  def require_lecturer
    redirect_to dashboard_path unless current_user&.lecturer?
  end

  def require_student
    redirect_to dashboard_path unless current_user&.student?
  end

end
