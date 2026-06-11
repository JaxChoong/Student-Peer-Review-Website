class CreateQuestionLayouts < ActiveRecord::Migration[8.1]
  def change
    create_table :question_layouts do |t|
      t.string :layout_name
      t.references :user, null: false, foreign_key: true

      t.timestamps
    end
  end
end
