import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = [ "toggle", "percentageContainer" ]

  connect() {
    this.toggleField()
  }

  toggleField() {
    if (!this.hasToggleTarget || !this.hasPercentageContainerTarget) return

    const isEnabled = this.toggleTarget.checked
    const container = this.percentageContainerTarget

    if (isEnabled) {
      container.classList.remove("max-h-0", "opacity-0")
      container.classList.add("max-h-20", "opacity-100")
    } else {
      container.classList.remove("max-h-20", "opacity-100")
      container.classList.add("max-h-0", "opacity-0")
    }
  }
}
