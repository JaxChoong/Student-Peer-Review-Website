import { Controller } from "@hotwired/stimulus"
import consumer from "channels/consumer"

export default class extends Controller {
  static values = { userId: String }

  connect() {
    if (!this.userIdValue) return;

    this.channel = consumer.subscriptions.create(
      { channel: "NotificationsChannel", user_id: this.userIdValue },
      {
        connected: () => {
          console.log("Connected to NotificationsChannel for user", this.userIdValue)
        },
        disconnected: () => {
          console.log("Disconnected from NotificationsChannel")
        },
        received: (data) => {
          this.showFlash(data)
        }
      }
    )
  }

  disconnect() {
    if (this.channel) {
      this.channel.unsubscribe()
    }
  }

  showFlash(data) {
    const flashContainer = this.element;
    
    // Create wrapper div
    const alertDiv = document.createElement("div");
    alertDiv.className = "mb-6 rounded-md px-4 py-3 text-sm font-medium ring-1 ring-inset ";
    
    if (data.type === "notice") {
      alertDiv.className += "bg-emerald-50 text-emerald-700 ring-emerald-600/20";
    } else if (data.type === "alert") {
      alertDiv.className += "bg-rose-50 text-rose-700 ring-rose-600/20";
    } else {
      alertDiv.className += "bg-blue-50 text-blue-700 ring-blue-600/20";
    }
    
    alertDiv.innerText = data.message;
    
    // Prepend to flash container so new messages appear at the top
    flashContainer.prepend(alertDiv);
    
    // Optionally remove it after a few seconds
    setTimeout(() => {
      alertDiv.remove();
    }, 5000);
  }
}
