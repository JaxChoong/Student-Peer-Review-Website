class AuthController < ApplicationController
  before_action :require_logout, only: [:new, :create, :login, :authenticate, :forgot_password, :send_reset, :reset_password, :confirm_reset]
  before_action :require_login, only: [:edit_password, :update_password, :destroy]

  # GET /register
  def new
    @user = User.new
  end

  # POST /register
  def create
    @user = User.new(user_params)
    
    # Assign role based on email domain
    if @user.email&.downcase&.include?('@mmu.')
      @user.role = 'lecturer'
    else
      @user.role = 'student'
    end

    if @user.save
      session[:user_id] = @user.id
      redirect_to dashboard_path, notice: "Account created successfully."
    else
      render :new, status: :unprocessable_entity
    end
  end

  # GET /login
  def login
  end

  # POST /login
  def authenticate
    user = User.find_by(email: params[:email])
    
    if user&.authenticate(params[:password])
      session[:user_id] = user.id
      redirect_to dashboard_path, notice: "Logged in successfully."
    else
      flash.now[:alert] = "Invalid email or password."
      render :login, status: :unprocessable_entity
    end
  end

  # DELETE /logout
  def destroy
    session.delete(:user_id)
    redirect_to root_path, notice: "Logged out successfully."
  end

  # GET /change_password
  def edit_password
  end

  # PATCH /change_password
  def update_password
    if current_user.authenticate(params[:current_password])
      if current_user.update(password: params[:new_password], password_confirmation: params[:password_confirmation])
        redirect_to dashboard_path, notice: "Password changed successfully."
      else
        render :edit_password, status: :unprocessable_entity
      end
    else
      flash.now[:alert] = "Current password is incorrect."
      render :edit_password, status: :unprocessable_entity
    end
  end

  # GET /forgot_password
  def forgot_password
  end

  # POST /forgot_password
  def send_reset
    if params[:email].present?
      user = User.find_by(email: params[:email])
      if user
        PasswordResetService.request_reset(user.email)
      end
      # Always show success to prevent email enumeration
      redirect_to login_path, notice: "If an account with that email exists, we have sent a password reset link."
    else
      flash.now[:alert] = "Please enter your email address."
      render :forgot_password, status: :unprocessable_entity
    end
  end

  # GET /reset_password/:token
  def reset_password
    @email = PasswordResetService.validate_token(params[:token])
    if @email.nil?
      redirect_to forgot_password_path, alert: "Invalid or expired password reset token."
    end
  end

  # PATCH /reset_password/:token
  def confirm_reset
    @email = PasswordResetService.validate_token(params[:token])
    
    if @email
      user = User.find_by(email: @email)
      if user.update(password: params[:password], password_confirmation: params[:password_confirmation])
        # Invalidate the token by destroying it
        PasswordReset.find_by(token: params[:token])&.destroy
        
        redirect_to login_path, notice: "Password has been reset successfully. Please log in."
      else
        render :reset_password, status: :unprocessable_entity
      end
    else
      redirect_to forgot_password_path, alert: "Invalid or expired password reset token."
    end
  end

  private

  def user_params
    params.require(:user).permit(:email, :name, :student_number, :password, :password_confirmation)
  end
end
