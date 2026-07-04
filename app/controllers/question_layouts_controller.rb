class QuestionLayoutsController < ApplicationController
  before_action :require_lecturer

  def index
    # Load system default layouts (user_id: nil) and the lecturer's own layouts
    @system_layouts = QuestionLayout.where(user_id: nil).includes(:questions)
    @my_layouts = current_user.question_layouts.includes(:questions)
  end

  def create
    @layout = current_user.question_layouts.build(layout_params)
    if @layout.save
      redirect_to customizations_path, notice: "Question layout created."
    else
      redirect_to customizations_path, alert: "Failed to create layout."
    end
  end

  def destroy
    @layout = current_user.question_layouts.find_by(id: params[:id])
    if @layout
      @layout.destroy
      redirect_to customizations_path, notice: "Layout deleted."
    else
      redirect_to customizations_path, alert: "Layout not found."
    end
  end

  def preview
    @course = current_user.courses.find_by(id: params[:course_id])
    return redirect_to dashboard_path, alert: "Course not found." unless @course

    render :preview
  end

  def update
    @layout = current_user.question_layouts.find_by(id: params[:id])
    if @layout
      if @layout.update(layout_params)
        redirect_to customizations_path, notice: "Layout updated successfully."
      else
        redirect_to customizations_path, alert: "Failed to update layout."
      end
    else
      redirect_to customizations_path, alert: "Layout not found."
    end
  end

  private

  def layout_params
    params.require(:question_layout).permit(:layout_name, questions_attributes: [:id, :question_text, :_destroy])
  end
end
