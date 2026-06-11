FactoryBot.define do
  factory :user, aliases: [:lecturer, :student, :reviewer, :reviewee] do
    sequence(:email) { |n| "user#{n}@example.com" }
    name { "Test User" }
    role { "student" }
    password { "password" }
  end

  factory :course do
    sequence(:course_code) { |n| "CS#{n}" }
    course_name { "Test Course" }
    lecturer
  end

  factory :section do
    sequence(:section_code) { |n| "S#{n}" }
    course
  end

  factory :group do
    sequence(:group_name) { |n| "Group #{n}" }
    course
    section
  end

  factory :enrollment do
    course
    section
    user
  end

  factory :group_membership do
    group
    user
  end

  factory :review do
    course
    section
    group
    reviewer
    reviewee
    score { 2.5 }
  end

  factory :question_layout do
    layout_name { "Test Layout" }
  end

  factory :question do
    question_layout
    question_text { "Test Question" }
  end

  factory :self_assessment do
    course
    question
    user
    question_text { "Test Question" }
    answer { "Test Answer" }
  end

  factory :lecturer_rating do
    lecturer
    student
    section
    rating { 2.5 }
  end

  factory :final_group_mark do
    group
    mark { 85.0 }
  end

  factory :password_reset do
    email { "test@example.com" }
    token { "secure_token" }
  end
end
