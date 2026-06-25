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

# Clear existing criteria to apply the updated seeds
rubric.rubric_criteria.destroy_all if rubric.rubric_criteria.any?

c1 = rubric.rubric_criteria.create!(label: "Attitude", position: 0)
attitude_bullets = [
  "Responds to and treats team members respectfully in communication.",
  "Uses a positive tone to convey a positive attitude about the team and its work.",
  "Demonstrates a willingness to compromise and adapt to team needs.",
  "Maintains professionalism and composure during challenging situations."
]
c1.rubric_columns.create!(weight: 4, position: 0, descriptions: ["Performs all of the following:"] + attitude_bullets)
c1.rubric_columns.create!(weight: 3, position: 1, descriptions: ["Performs any three of the following:"] + attitude_bullets)
c1.rubric_columns.create!(weight: 2, position: 2, descriptions: ["Performs any two of the following:"] + attitude_bullets)
c1.rubric_columns.create!(weight: 1, position: 3, descriptions: ["Performs only one of the following:"] + attitude_bullets)

c2 = rubric.rubric_criteria.create!(label: "Teamwork", position: 1)
teamwork_bullets = [
  "Offers ideas, provides assistance, or gives encouragement to team members.",
  "Completes a fair share of the work within timelines agreed by the team.",
  "Actively participates in team meetings and collaborative decision-making.",
  "Consistently reviews and integrates feedback from peers to improve the project."
]
c2.rubric_columns.create!(weight: 4, position: 0, descriptions: ["Performs all of the following:"] + teamwork_bullets)
c2.rubric_columns.create!(weight: 3, position: 1, descriptions: ["Performs any three of the following:"] + teamwork_bullets)
c2.rubric_columns.create!(weight: 2, position: 2, descriptions: ["Performs any two of the following:"] + teamwork_bullets)
c2.rubric_columns.create!(weight: 1, position: 3, descriptions: ["Performs only one of the following:"] + teamwork_bullets)
puts "Created default RubricTemplate"

require 'csv'

puts "Seeding example students..."
csv_path = Rails.root.join('example.csv')
if File.exist?(csv_path)
  CSV.foreach(csv_path, headers: true) do |row|
    User.find_or_create_by!(email: row['email']) do |u|
      u.name = row['name']
      u.student_number = row['studentId']
      u.password = "password123"
      u.password_confirmation = "password123"
      u.role = 'student'
    end
  end
  puts "Created example students from example.csv"
else
  puts "example.csv not found, skipping student seeding."
end

puts "Seeding test lecturer..."
User.find_or_create_by!(email: "testlecturer@mmu.edu.my") do |u|
  u.name = "Test Lecturer"
  u.password = "password123"
  u.password_confirmation = "password123"
  u.role = 'lecturer'
end
puts "Created test lecturer"

puts "Seeding complete!"
