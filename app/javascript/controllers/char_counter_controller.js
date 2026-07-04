import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["input", "indicator"]
  static values = { min: Number, max: Number }

  connect() {
    this.updateIndicator()
  }

  updateIndicator() {
    const length = this.inputTarget.value.length
    
    // Only show if focused
    if (document.activeElement !== this.inputTarget) {
      this.hide()
      return
    }

    if (length < this.minValue) {
      const remaining = this.minValue - length
      this.indicatorTarget.textContent = `${remaining} more`
      this.indicatorTarget.classList.remove('text-rose-500', 'text-amber-500')
      this.indicatorTarget.classList.add('text-slate-400')
      this.show()
    } else if (this.hasMaxValue && length >= this.maxValue - 20) {
      const remaining = this.maxValue - length
      this.indicatorTarget.textContent = `${remaining} left`
      this.indicatorTarget.classList.remove('text-slate-400')
      if (remaining <= 5) {
        this.indicatorTarget.classList.add('text-rose-500')
        this.indicatorTarget.classList.remove('text-amber-500')
      } else {
        this.indicatorTarget.classList.add('text-amber-500')
        this.indicatorTarget.classList.remove('text-rose-500')
      }
      this.show()
    } else {
      this.hide()
    }
  }

  show() {
    this.indicatorTarget.classList.remove('opacity-0')
    this.indicatorTarget.classList.add('opacity-100')
  }

  hide() {
    this.indicatorTarget.classList.remove('opacity-100')
    this.indicatorTarget.classList.add('opacity-0')
  }
}
