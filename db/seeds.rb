# This file should ensure the existence of records required to run the application in every environment (production,
# development, test). The code here should be idempotent so that it can be executed at any point in every environment.
# The data can then be loaded with the bin/rails db:seed command (or created alongside the database with db:setup).
#
# Example:
#
#   ["Action", "Comedy", "Drama", "Horror"].each do |genre_name|
#     MovieGenre.find_or_create_by!(name: genre_name)
#   end

puts "Seeding default data..."

# Default Introduction
intro = Introduction.find_or_create_by!(
  content: "Welcome to the Student Peer Review system. Please review your peers fairly and honestly based on their contributions to the project."
)
puts "Created default Introduction"

# Default Question Layout
layout = QuestionLayout.find_or_create_by!(
  layout_name: "Default Peer Review Layout",
  user_id: nil # System default
)
puts "Created default QuestionLayout"

# Default Questions
[
  "Rate the member's communication skills.",
  "Rate the member's technical contribution.",
  "Rate the member's teamwork and collaboration.",
  "Rate the member's overall contribution to the project."
].each do |q_text|
  Question.find_or_create_by!(
    question_layout: layout,
    question_text: q_text
  )
end
puts "Created default Questions"

puts "Seeding complete!"
