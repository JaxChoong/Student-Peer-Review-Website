class PagesController < ApplicationController
  def landing
    redirect_to dashboard_path if current_user
  end

  def about_us
  end

  def example_csv
    send_file Rails.root.join('example.csv'), type: 'text/csv', filename: 'example.csv'
  end
end
