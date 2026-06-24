import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["reviewModeSelect", "scoringSchemeSelect", "helperText"]

  connect() {
    this.toggleScoringScheme()
  }

  toggleScoringScheme() {
    if (!this.hasReviewModeSelectTarget || !this.hasScoringSchemeSelectTarget) return
    
    const reviewModeSelect = this.reviewModeSelectTarget
    const selectedReviewMode = reviewModeSelect.options[reviewModeSelect.selectedIndex].text
    const isHybrid = selectedReviewMode.includes("Hybrid")
    
    const schemeSelect = this.scoringSchemeSelectTarget
    
    // Find the options
    let rubricOptionIndex = -1
    let pointPoolOptionIndex = -1
    for (let i = 0; i < schemeSelect.options.length; i++) {
      if (schemeSelect.options[i].text.includes("Rubric")) {
        rubricOptionIndex = i
      }
      if (schemeSelect.options[i].text.includes("Point Pool")) {
        pointPoolOptionIndex = i
      }
    }
    
    if (isHybrid) {
      // Hybrid Mode: Hide Rubric, Show Point Pool
      if (rubricOptionIndex !== -1) {
        schemeSelect.options[rubricOptionIndex].disabled = true
        schemeSelect.options[rubricOptionIndex].hidden = true
        // Switch to Numeric if Rubric is selected
        if (schemeSelect.selectedIndex === rubricOptionIndex) {
          schemeSelect.selectedIndex = 0
        }
      }
      if (pointPoolOptionIndex !== -1) {
        schemeSelect.options[pointPoolOptionIndex].disabled = false
        schemeSelect.options[pointPoolOptionIndex].hidden = false
      }
      
      schemeSelect.removeAttribute("disabled")
      schemeSelect.classList.remove("bg-slate-100", "cursor-not-allowed", "text-slate-500")
      schemeSelect.classList.add("bg-white", "text-slate-900")
      

    } else {
      // Peer Ratings Only Mode: Hide Point Pool, Show Rubric
      if (pointPoolOptionIndex !== -1) {
        schemeSelect.options[pointPoolOptionIndex].disabled = true
        schemeSelect.options[pointPoolOptionIndex].hidden = true
        // Switch to Numeric if Point Pool is selected
        if (schemeSelect.selectedIndex === pointPoolOptionIndex) {
          schemeSelect.selectedIndex = 0
        }
      }
      if (rubricOptionIndex !== -1) {
        schemeSelect.options[rubricOptionIndex].disabled = false
        schemeSelect.options[rubricOptionIndex].hidden = false
      }
      
      schemeSelect.removeAttribute("disabled")
      schemeSelect.classList.remove("bg-slate-100", "cursor-not-allowed", "text-slate-500")
      schemeSelect.classList.add("bg-white", "text-slate-900")
      

    }
  }
}
