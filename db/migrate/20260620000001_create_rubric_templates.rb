class CreateRubricTemplates < ActiveRecord::Migration[8.1]
  def change
    create_table :rubric_templates do |t|
      t.references :user, null: true, foreign_key: true
      t.string :template_name, null: false

      t.timestamps
    end
  end
end
