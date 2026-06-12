Rails.application.routes.draw do
  root "pages#landing"

  # ── Auth ──────────────────────────────────────────────
  get  "/register",                   to: "auth#new"
  post "/register",                   to: "auth#create"
  get  "/login",                      to: "auth#login"
  post "/login",                      to: "auth#authenticate"
  delete "/logout",                   to: "auth#destroy"
  get  "/change_password",            to: "auth#edit_password"
  patch "/change_password",           to: "auth#update_password"
  get  "/forgot_password",            to: "auth#forgot_password"
  post "/forgot_password",            to: "auth#send_reset"
  get  "/reset_password/:token",      to: "auth#reset_password",   as: :reset_password
  patch "/reset_password/:token",     to: "auth#confirm_reset"

  # ── General ───────────────────────────────────────────
  get "/dashboard",                   to: "dashboard#index"
  get "/about_us",                    to: "pages#about_us"
  get "/example_csv",                 to: "pages#example_csv"

  # ── Courses (Lecturer) ────────────────────────────────
  resources :courses, only: [:new, :create, :destroy] do
    member do
      patch :update_intro
      patch :update_review_dates
      patch :update_layout
    end
    resources :groups, only: [:index, :show]
  end

  # ── Sections (Lecturer) ───────────────────────────────
  patch "/sections/:id/review_dates", to: "sections#update_review_dates", as: :update_review_dates_section

  # ── Question Layouts (Lecturer) ───────────────────────
  get  "/customizations",             to: "question_layouts#index"
  post "/question_layouts",           to: "question_layouts#create"
  delete "/question_layouts/:id",     to: "question_layouts#destroy", as: :question_layout
  post "/question_layouts/:question_layout_id/questions", to: "questions#create", as: :question_layout_questions
  delete "/question_layouts/:question_layout_id/questions/:id", to: "questions#destroy", as: :question_layout_question
  get "/preview_layout",             to: "question_layouts#preview"
  post "/preview_layout/switch",      to: "question_layouts#switch_preview"

  # ── Peer Reviews (Student) ────────────────────────────
  get "/courses/:course_id/peer_reviews/start", to: "peer_reviews#start", as: :course_peer_reviews_start
  post "/courses/:course_id/peer_reviews/submit", to: "peer_reviews#submit", as: :course_peer_reviews_submit

  # Define your application routes per the DSL in https://guides.rubyonrails.org/routing.html

  # Reveal health status on /up that returns 200 if the app boots with no exceptions, otherwise 500.
  # Can be used by load balancers and uptime monitors to verify that the app is live.
  get "up" => "rails/health#show", as: :rails_health_check

  # Render dynamic PWA files from app/views/pwa/* (remember to link manifest in application.html.erb)
  # get "manifest" => "rails/pwa#manifest", as: :pwa_manifest
  # get "service-worker" => "rails/pwa#service_worker", as: :pwa_service_worker

  # Defines the root path route ("/")
  # root "posts#index"
end
