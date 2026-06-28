class AddAllowPeerSelfReviewToCourses < ActiveRecord::Migration[8.1]
  def change
    add_column :courses, :allow_peer_self_review, :boolean, default: true, null: false
  end
end
