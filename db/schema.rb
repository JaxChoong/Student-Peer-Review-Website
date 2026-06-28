# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[8.1].define(version: 2026_06_28_022408) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "pg_catalog.plpgsql"

  create_table "courses", force: :cascade do |t|
    t.boolean "allow_peer_self_review", default: true, null: false
    t.string "course_code"
    t.string "course_name"
    t.datetime "created_at", null: false
    t.date "end_date"
    t.bigint "introduction_id"
    t.bigint "lecturer_id", null: false
    t.text "pending_credentials_csv"
    t.bigint "question_layout_id"
    t.boolean "require_self_review", default: true, null: false
    t.integer "review_mode", default: 0, null: false
    t.bigint "rubric_template_id"
    t.integer "scoring_scheme", default: 0, null: false
    t.date "start_date"
    t.datetime "updated_at", null: false
    t.index ["course_code"], name: "index_courses_on_course_code", unique: true
    t.index ["introduction_id"], name: "index_courses_on_introduction_id"
    t.index ["lecturer_id"], name: "index_courses_on_lecturer_id"
    t.index ["question_layout_id"], name: "index_courses_on_question_layout_id"
    t.index ["rubric_template_id"], name: "index_courses_on_rubric_template_id"
  end

  create_table "enrollments", force: :cascade do |t|
    t.bigint "course_id", null: false
    t.datetime "created_at", null: false
    t.bigint "section_id", null: false
    t.datetime "updated_at", null: false
    t.bigint "user_id", null: false
    t.index ["course_id", "section_id", "user_id"], name: "index_enrollments_on_course_id_and_section_id_and_user_id", unique: true
    t.index ["course_id"], name: "index_enrollments_on_course_id"
    t.index ["section_id"], name: "index_enrollments_on_section_id"
    t.index ["user_id"], name: "index_enrollments_on_user_id"
  end

  create_table "final_group_marks", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.bigint "group_id", null: false
    t.decimal "mark", precision: 6, scale: 2
    t.datetime "updated_at", null: false
    t.index ["group_id"], name: "index_final_group_marks_on_group_id", unique: true
  end

  create_table "group_memberships", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.bigint "group_id", null: false
    t.datetime "updated_at", null: false
    t.bigint "user_id", null: false
    t.index ["group_id", "user_id"], name: "index_group_memberships_on_group_id_and_user_id", unique: true
    t.index ["group_id"], name: "index_group_memberships_on_group_id"
    t.index ["user_id"], name: "index_group_memberships_on_user_id"
  end

  create_table "groups", force: :cascade do |t|
    t.bigint "course_id", null: false
    t.datetime "created_at", null: false
    t.string "group_name"
    t.bigint "section_id", null: false
    t.datetime "updated_at", null: false
    t.index ["course_id"], name: "index_groups_on_course_id"
    t.index ["section_id"], name: "index_groups_on_section_id"
  end

  create_table "introductions", force: :cascade do |t|
    t.text "content"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "lecturer_ratings", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.bigint "lecturer_id", null: false
    t.decimal "rating", precision: 5, scale: 2
    t.bigint "section_id", null: false
    t.bigint "student_id", null: false
    t.datetime "updated_at", null: false
    t.index ["lecturer_id", "student_id", "section_id"], name: "index_lecturer_ratings_on_unique_rating", unique: true
    t.index ["lecturer_id"], name: "index_lecturer_ratings_on_lecturer_id"
    t.index ["section_id"], name: "index_lecturer_ratings_on_section_id"
    t.index ["student_id"], name: "index_lecturer_ratings_on_student_id"
  end

  create_table "password_resets", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.string "email"
    t.string "token"
    t.datetime "updated_at", null: false
    t.index ["token"], name: "index_password_resets_on_token", unique: true
  end

  create_table "question_layouts", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.string "layout_name"
    t.datetime "updated_at", null: false
    t.bigint "user_id"
    t.index ["user_id"], name: "index_question_layouts_on_user_id"
  end

  create_table "questions", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.bigint "question_layout_id", null: false
    t.text "question_text"
    t.datetime "updated_at", null: false
    t.index ["question_layout_id"], name: "index_questions_on_question_layout_id"
  end

  create_table "reviews", force: :cascade do |t|
    t.text "comment"
    t.bigint "course_id", null: false
    t.datetime "created_at", null: false
    t.bigint "group_id", null: false
    t.bigint "reviewee_id", null: false
    t.bigint "reviewer_id", null: false
    t.decimal "score", precision: 5, scale: 2, null: false
    t.bigint "section_id", null: false
    t.datetime "updated_at", null: false
    t.index ["course_id", "section_id", "group_id", "reviewer_id", "reviewee_id"], name: "index_reviews_on_unique_review", unique: true
    t.index ["course_id"], name: "index_reviews_on_course_id"
    t.index ["group_id"], name: "index_reviews_on_group_id"
    t.index ["reviewee_id"], name: "index_reviews_on_reviewee_id"
    t.index ["reviewer_id"], name: "index_reviews_on_reviewer_id"
    t.index ["section_id"], name: "index_reviews_on_section_id"
  end

  create_table "rubric_columns", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.text "descriptions", default: [], array: true
    t.integer "position", default: 0, null: false
    t.bigint "rubric_criteria_id", null: false
    t.datetime "updated_at", null: false
    t.integer "weight", null: false
    t.index ["rubric_criteria_id"], name: "index_rubric_columns_on_rubric_criteria_id"
  end

  create_table "rubric_criteria", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.string "label", null: false
    t.integer "position", default: 0, null: false
    t.bigint "rubric_template_id", null: false
    t.datetime "updated_at", null: false
    t.index ["rubric_template_id"], name: "index_rubric_criteria_on_rubric_template_id"
  end

  create_table "rubric_scores", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.string "criteria_label_snapshot", null: false
    t.integer "position", default: 0, null: false
    t.bigint "review_id", null: false
    t.bigint "rubric_criteria_id"
    t.integer "selected_weight", null: false
    t.datetime "updated_at", null: false
    t.index ["review_id"], name: "index_rubric_scores_on_review_id"
    t.index ["rubric_criteria_id"], name: "index_rubric_scores_on_rubric_criteria_id"
  end

  create_table "rubric_templates", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.string "template_name", null: false
    t.datetime "updated_at", null: false
    t.bigint "user_id"
    t.index ["user_id"], name: "index_rubric_templates_on_user_id"
  end

  create_table "sections", force: :cascade do |t|
    t.bigint "course_id", null: false
    t.datetime "created_at", null: false
    t.date "end_date"
    t.string "section_code"
    t.date "start_date"
    t.datetime "updated_at", null: false
    t.index ["course_id"], name: "index_sections_on_course_id"
  end

  create_table "self_assessments", force: :cascade do |t|
    t.text "answer"
    t.bigint "course_id", null: false
    t.datetime "created_at", null: false
    t.bigint "question_id", null: false
    t.text "question_text"
    t.datetime "updated_at", null: false
    t.bigint "user_id", null: false
    t.index ["course_id", "question_id", "user_id"], name: "index_self_assessments_on_unique_submission", unique: true
    t.index ["course_id"], name: "index_self_assessments_on_course_id"
    t.index ["question_id"], name: "index_self_assessments_on_question_id"
    t.index ["user_id"], name: "index_self_assessments_on_user_id"
  end

  create_table "users", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.string "email", null: false
    t.string "name", null: false
    t.string "password_digest", null: false
    t.string "role", null: false
    t.string "student_number"
    t.datetime "updated_at", null: false
    t.index ["email"], name: "index_users_on_email", unique: true
  end

  add_foreign_key "courses", "introductions"
  add_foreign_key "courses", "question_layouts"
  add_foreign_key "courses", "rubric_templates"
  add_foreign_key "courses", "users", column: "lecturer_id"
  add_foreign_key "enrollments", "courses"
  add_foreign_key "enrollments", "sections"
  add_foreign_key "enrollments", "users"
  add_foreign_key "final_group_marks", "groups"
  add_foreign_key "group_memberships", "groups"
  add_foreign_key "group_memberships", "users"
  add_foreign_key "groups", "courses"
  add_foreign_key "groups", "sections"
  add_foreign_key "lecturer_ratings", "sections"
  add_foreign_key "lecturer_ratings", "users", column: "lecturer_id"
  add_foreign_key "lecturer_ratings", "users", column: "student_id"
  add_foreign_key "question_layouts", "users"
  add_foreign_key "questions", "question_layouts"
  add_foreign_key "reviews", "courses"
  add_foreign_key "reviews", "groups"
  add_foreign_key "reviews", "sections"
  add_foreign_key "reviews", "users", column: "reviewee_id"
  add_foreign_key "reviews", "users", column: "reviewer_id"
  add_foreign_key "rubric_columns", "rubric_criteria", column: "rubric_criteria_id"
  add_foreign_key "rubric_criteria", "rubric_templates"
  add_foreign_key "rubric_scores", "reviews"
  add_foreign_key "rubric_scores", "rubric_criteria", column: "rubric_criteria_id"
  add_foreign_key "rubric_templates", "users"
  add_foreign_key "sections", "courses"
  add_foreign_key "self_assessments", "courses"
  add_foreign_key "self_assessments", "questions"
  add_foreign_key "self_assessments", "users"
end
