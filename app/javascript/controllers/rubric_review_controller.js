import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["cell", "hiddenInput"]
  static values = { memberId: Number }

  connect() {
    this.validateForm()
  }

  select(event) {
    event.preventDefault()
    
    const clickedCell = event.currentTarget
    const memberId = clickedCell.dataset.member
    const criteriaId = clickedCell.dataset.criteria
    const weight = clickedCell.dataset.weight

    // Deselect other cells in the same row
    this.cellTargets.forEach(cell => {
      if (cell.dataset.member === memberId && cell.dataset.criteria === criteriaId) {
        cell.classList.remove('ring-2', 'ring-blue-600', 'bg-blue-50', 'border-blue-500')
        cell.classList.add('border-slate-200', 'bg-white')
      }
    })

    // Select clicked cell
    clickedCell.classList.remove('border-slate-200', 'bg-white')
    clickedCell.classList.add('ring-2', 'ring-blue-600', 'bg-blue-50', 'border-blue-500')

    // Update hidden input
    const input = this.hiddenInputTargets.find(i => i.id === `rubric_${memberId}_${criteriaId}_weight`)
    if (input) {
      input.value = weight
    }

    this.validateForm()
  }

  validateForm() {
    // Check if all hidden inputs have a value
    const allFilled = this.hiddenInputTargets.every(input => input.value !== "")
    
    const submitBtn = document.getElementById('submit-peer-review-btn')
    if (submitBtn) {
      if (allFilled) {
        submitBtn.disabled = false
        submitBtn.classList.remove('opacity-50', 'cursor-not-allowed')
      } else {
        submitBtn.disabled = true
        submitBtn.classList.add('opacity-50', 'cursor-not-allowed')
      }
    }
  }
}
