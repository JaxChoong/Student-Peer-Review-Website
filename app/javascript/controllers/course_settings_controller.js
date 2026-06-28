import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = [
    "reviewModeSelect", 
    "scoringSchemeSelect", 
    "helperText",
    "selfReviewToggle",
    "selfReviewTemplateContainer",
    "selfReviewTemplateSelect",
    "rubricTemplateContainer",
    "rubricTemplateSelect"
  ]

  connect() {
    this.toggleScoringScheme()
    if (this.hasSelfReviewToggleTarget) {
      this.toggleSelfReviewTemplate()
    }
    if (this.hasScoringSchemeSelectTarget) {
      this.toggleRubricTemplate()
    }
  }

  toggleScoringScheme() {
    if (!this.hasReviewModeSelectTarget || !this.hasScoringSchemeSelectTarget) return
    
    const reviewModeSelect = this.reviewModeSelectTarget
    const selectedReviewMode = reviewModeSelect.options[reviewModeSelect.selectedIndex].text
    const isNormalised = selectedReviewMode.includes("Normalised")
    
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
    
    let schemeChanged = false

    if (isNormalised) {
      // Normalised Mode: Hide Rubric, Show Point Pool
      if (rubricOptionIndex !== -1) {
        schemeSelect.options[rubricOptionIndex].disabled = true
        schemeSelect.options[rubricOptionIndex].hidden = true
        // Switch to Numeric if Rubric is selected
        if (schemeSelect.selectedIndex === rubricOptionIndex) {
          schemeSelect.selectedIndex = 0
          schemeChanged = true
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
      // Raw Peer Ratings Mode: Hide Point Pool, Show Rubric
      if (pointPoolOptionIndex !== -1) {
        schemeSelect.options[pointPoolOptionIndex].disabled = true
        schemeSelect.options[pointPoolOptionIndex].hidden = true
        // Switch to Numeric if Point Pool is selected
        if (schemeSelect.selectedIndex === pointPoolOptionIndex) {
          schemeSelect.selectedIndex = 0
          schemeChanged = true
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

    if (schemeChanged) {
      this.toggleRubricTemplate()
    }
  }

  toggleSelfReviewTemplate() {
    if (!this.hasSelfReviewToggleTarget || !this.hasSelfReviewTemplateContainerTarget || !this.hasSelfReviewTemplateSelectTarget) return

    const isEnabled = this.selfReviewToggleTarget.checked
    if (isEnabled) {
      this.selfReviewTemplateContainerTarget.classList.remove("hidden")
      this.selfReviewTemplateSelectTarget.required = true
    } else {
      this.selfReviewTemplateContainerTarget.classList.add("hidden")
      this.selfReviewTemplateSelectTarget.required = false
      this.selfReviewTemplateSelectTarget.value = ""
    }
  }

  toggleRubricTemplate() {
    if (!this.hasScoringSchemeSelectTarget || !this.hasRubricTemplateContainerTarget || !this.hasRubricTemplateSelectTarget) return

    const schemeSelect = this.scoringSchemeSelectTarget
    const isRubric = schemeSelect.options[schemeSelect.selectedIndex].text.includes("Rubric")

    if (isRubric) {
      this.rubricTemplateContainerTarget.classList.remove("hidden")
      this.rubricTemplateSelectTarget.required = true
    } else {
      this.rubricTemplateContainerTarget.classList.add("hidden")
      this.rubricTemplateSelectTarget.required = false
      this.rubricTemplateSelectTarget.value = ""
    }
  }
}
