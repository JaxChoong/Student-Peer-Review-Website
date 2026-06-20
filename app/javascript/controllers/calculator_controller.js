import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = [
    "groupMarkInput", "peerRatingInput", "lecturerRatingInput", "submittedReviewsCheckbox",
    "groupMarkVal", "peerRatingVal", "lecturerRatingVal", "finalCalculatedVal", "calcExplanation"
  ]

  connect() {
    if (this.hasGroupMarkInputTarget) {
      this.updateCalculator()
    }
  }

  updateCalculator() {
    const am = parseFloat(this.groupMarkInputTarget.value)
    const apr = parseFloat(this.peerRatingInputTarget.value)
    const le = parseFloat(this.lecturerRatingInputTarget.value)
    const submitted = this.submittedReviewsCheckboxTarget.checked

    // Update Slider Labels
    this.groupMarkValTarget.textContent = am + "%"
    this.peerRatingValTarget.textContent = apr.toFixed(1) + " / 3.0"
    this.lecturerRatingValTarget.textContent = le.toFixed(1) + " / 3.0"

    if (!submitted) {
      this.finalCalculatedValTarget.textContent = "0.00%"
      this.finalCalculatedValTarget.className = "mt-2 text-5xl font-extrabold text-rose-500"
      this.calcExplanationTarget.innerHTML = "<span class='text-rose-400 font-bold'>Penalty Applied:</span> Student did not submit any reviews."
      return
    }

    const aprRatio = apr / 3.0
    const leRatio = le / 3.0
    const finalMark = (0.5 * am) + (0.25 * am * aprRatio) + (0.25 * am * leRatio)

    this.finalCalculatedValTarget.textContent = finalMark.toFixed(2) + "%"
    this.finalCalculatedValTarget.className = "mt-2 text-5xl font-extrabold text-blue-400"
    this.calcExplanationTarget.innerHTML = `Calculation: (0.50 × ${am.toFixed(2)}) + (0.25 × ${am.toFixed(2)} × (${apr.toFixed(2)} / 3.0)) + (0.25 × ${am.toFixed(2)} × (${le.toFixed(2)} / 3.0))`
  }
}
