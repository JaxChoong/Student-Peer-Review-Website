import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["reviewModeSelect", "scoringSchemeSelect", "helperText"]

  connect() {
    this.toggleScoringScheme()
  }

  toggleScoringScheme() {
    if (!this.hasReviewModeSelectTarget || !this.hasScoringSchemeSelectTarget) return

    const isHybrid = this.reviewModeSelectTarget.value === "1"

    if (isHybrid) {
      // Force Numeric
      this.scoringSchemeSelectTarget.value = "0"
      
      // Make it appear disabled / readonly via styling
      this.scoringSchemeSelectTarget.classList.add("bg-slate-100", "cursor-not-allowed", "text-slate-500")
      this.scoringSchemeSelectTarget.classList.remove("bg-white", "text-slate-900")
      
      // Actually disable it to prevent changes
      this.scoringSchemeSelectTarget.setAttribute("disabled", "disabled")
      
      if (this.hasHelperTextTarget) {
        this.helperTextTarget.classList.remove("hidden")
      }
    } else {
      // Enable selection again
      this.scoringSchemeSelectTarget.classList.remove("bg-slate-100", "cursor-not-allowed", "text-slate-500")
      this.scoringSchemeSelectTarget.classList.add("bg-white", "text-slate-900")
      
      this.scoringSchemeSelectTarget.removeAttribute("disabled")
      
      if (this.hasHelperTextTarget) {
        this.helperTextTarget.classList.add("hidden")
      }
    }
  }
}
