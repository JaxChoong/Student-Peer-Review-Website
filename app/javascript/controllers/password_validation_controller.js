import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["input", "hint"]

  connect() {
    if (this.hasInputTarget && this.hasHintTarget) {
      this.updateHint()
    }
  }

  updateHint() {
    const val = this.inputTarget.value
    const hint = this.hintTarget

    if (val.length === 0) {
      hint.textContent = "Must be at least 6 characters long."
      hint.className = "mt-1.5 text-[11px] font-medium text-slate-500"
    } else if (val.length < 6) {
      hint.textContent = "⚠️ Too short (must be at least 6 characters)."
      hint.className = "mt-1.5 text-[11px] font-semibold text-rose-600 animate-pulse"
    } else {
      hint.textContent = "✓ Valid format length."
      hint.className = "mt-1.5 text-[11px] font-bold text-emerald-600"
    }
  }
}
