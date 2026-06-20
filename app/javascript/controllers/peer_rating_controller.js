import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["input", "normalizeBtn", "submitBtn", "warning", "badge"]

  connect() {
    if (this.hasSubmitBtnTarget) {
      this.submitBtnTarget.disabled = true
    }
  }

  inputChanged(event) {
    const input = event.currentTarget
    
    // Strip decimals/non-digits
    input.value = input.value.replace(/[^0-9]/g, '')
    
    // Clamp to 1-5
    if (parseInt(input.value) > 5) input.value = 5
    if (parseInt(input.value) < 1) input.value = 1
    
    if (this.hasSubmitBtnTarget) {
      this.submitBtnTarget.disabled = true
      this.submitBtnTarget.classList.add('opacity-50', 'cursor-not-allowed')
    }
    
    if (this.hasWarningTarget) {
      this.warningTarget.classList.remove('hidden')
    }
    
    this.badgeTargets.forEach(badge => {
      badge.classList.add('hidden')
      badge.classList.remove('flex')
    })
  }

  normalize() {
    let total = 0
    let allFilled = true
    const numStudents = this.inputTargets.length

    this.inputTargets.forEach(input => {
      const val = parseInt(input.value)
      if (isNaN(val)) {
        allFilled = false
      } else {
        total += val
      }
    })

    if (!allFilled || total === 0) {
      alert("Please provide a valid rating (1-5) for everyone before normalizing.")
      return
    }

    // Calculate and display
    this.inputTargets.forEach(input => {
      const val = parseInt(input.value)
      const adjusted = ((val / total) * 3.0 * numStudents).toFixed(2)
      
      const badgeId = input.name.match(/reviews\[(\d+)\]\[score\]/)[1]
      const badge = this.badgeTargets.find(b => b.id === `adjusted-score-${badgeId}`)
      
      if (badge) {
        badge.textContent = adjusted
        badge.classList.remove('hidden')
        badge.classList.add('flex')
      }
    })

    if (this.hasSubmitBtnTarget) {
      this.submitBtnTarget.disabled = false
      this.submitBtnTarget.classList.remove('opacity-50', 'cursor-not-allowed')
    }
    
    if (this.hasWarningTarget) {
      this.warningTarget.classList.add('hidden')
    }
  }
}
