class CreateIntroductions < ActiveRecord::Migration[8.1]
  def change
    create_table :introductions do |t|
      t.text :content

      t.timestamps
    end
  end
end
