class CreateSelfAssessments < ActiveRecord::Migration[8.1]
  def change
    create_table :self_assessments do |t|
      t.references :course, null: false, foreign_key: true
      t.references :question, null: false, foreign_key: true
      t.text :question_text
      t.text :answer
      t.references :user, null: false, foreign_key: true

      t.timestamps
    end
    add_index :self_assessments, [:course_id, :question_id, :user_id], unique: true, name: 'index_self_assessments_on_unique_submission'
  end
end
