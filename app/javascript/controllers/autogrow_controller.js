import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  connect() {
    this.element.style.overflow = 'hidden'
    setTimeout(() => this.resize(), 10)
  }

  resize() {
    this.element.style.height = 'auto'
    this.element.style.height = this.element.scrollHeight + 'px'
  }
}
