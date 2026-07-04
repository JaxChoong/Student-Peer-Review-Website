import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["view", "form"]

  toggle(event) {
    if (event) event.preventDefault()
    
    this.viewTarget.classList.toggle("hidden")
    this.formTarget.classList.toggle("hidden")
  }
}
