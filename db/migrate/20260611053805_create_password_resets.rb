class CreatePasswordResets < ActiveRecord::Migration[8.1]
  def change
    create_table :password_resets do |t|
      t.string :email
      t.string :token

      t.timestamps
    end
    add_index :password_resets, :token, unique: true
  end
end
