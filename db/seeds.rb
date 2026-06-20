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
  "Describe your communication skills and how they impacted the group.",
  "Describe your technical contribution to the project.",
  "Describe your teamwork and collaboration.",
  "Describe your overall contribution to the project."
].each do |q_text|
  Question.find_or_create_by!(
    question_layout: layout,
    question_text: q_text
  )
end
puts "Created default Questions"

# Default Rubric Template
rubric = RubricTemplate.find_or_create_by!(
  template_name: "Default Peer Review Rubric",
  user_id: nil # System default
)

if rubric.rubric_criteria.empty?
  c1 = rubric.rubric_criteria.create!(label: "Attitude", position: 0)
  c1.rubric_columns.create!(weight: 4, position: 0, descriptions: ["Performs all the following: ", "Treats team members respectfully in communication.", "Uses a positive tone to convey positive attitude about the team.", "Motivates teammates by expressing confidence about the team's ability.", "Helps and/or encouragement to team members."])
  c1.rubric_columns.create!(weight: 3, position: 1, descriptions: ["Performs three of the following: ", "Treats team members respectfully in communication.", "Uses a positive tone to convey positive attitude about the team.", "Motivates teammates by expressing confidence about the team's ability.", "Helps and/or encouragement to team members."])
  c1.rubric_columns.create!(weight: 2, position: 2, descriptions: ["Performs two of the following: ", "Treats team members respectfully in communication.", "Uses a positive tone to convey positive attitude about the team.", "Motivates teammates by expressing confidence about the team's ability.", "Helps and/or encouragement to team members."])
  c1.rubric_columns.create!(weight: 1, position: 3, descriptions: ["Performs one of the following: ", "Treats team members respectfully in communication.", "Uses a positive tone to convey positive attitude about the team.", "Motivates teammates by expressing confidence about the team's ability.", "Helps and/or encouragement to team members."])

  c2 = rubric.rubric_criteria.create!(label: "Role in Team", position: 1)
  c2.rubric_columns.create!(weight: 4, position: 0, descriptions: ["This member is (one) our most valuable player(s) and helps carry the whole team to success. Offers valuable insight and assistance to others to improve play and work."])
  c2.rubric_columns.create!(weight: 3, position: 1, descriptions: ["This member is a valuable member of the team and fulfils their role to help ensure our success as a team."])
  c2.rubric_columns.create!(weight: 2, position: 2, descriptions: ["This member fulfils their role but could have put more effort into helping us succeed as a team."])
  c2.rubric_columns.create!(weight: 1, position: 3, descriptions: ["This member is either passive and does not contribute, or actively sabotages our play and work."])
end
puts "Created default RubricTemplate"

puts "Seeding complete!"
