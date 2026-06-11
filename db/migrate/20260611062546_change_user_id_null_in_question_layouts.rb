class ChangeUserIdNullInQuestionLayouts < ActiveRecord::Migration[8.1]
  def change
    change_column_null :question_layouts, :user_id, true
  end
end
