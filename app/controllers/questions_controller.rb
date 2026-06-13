class QuestionsController < ApplicationController
  before_action :require_lecturer

  def create
    @layout = current_user.question_layouts.find_by(id: params[:question_layout_id])
    return redirect_to customizations_path, alert: "Layout not found." unless @layout

    @question = @layout.questions.build(question_params)
    if @question.save
      redirect_to customizations_path, notice: "Question added."
    else
      redirect_to customizations_path, alert: "Failed to add question."
    end
  end

  def destroy
    @layout = current_user.question_layouts.find_by(id: params[:question_layout_id])
    return redirect_to customizations_path, alert: "Layout not found." unless @layout

    @question = @layout.questions.find_by(id: params[:id])
    if @question
      @question.destroy
      redirect_to customizations_path, notice: "Question removed."
    else
      redirect_to customizations_path, alert: "Question not found."
    end
  end

  private

  def question_params
    params.require(:question).permit(:question_text)
  end
end
