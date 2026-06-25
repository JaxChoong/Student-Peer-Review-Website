import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["input", "submitBtn", "inlinePanel", "inlineCounter", "floatingPanel", "floatingCounter"]

  connect() {
    // Store direct references before teleporting the floating panel to <body>
    // (Stimulus loses target tracking once the element leaves the controller's DOM scope)
    this._floatingPanel = this.hasFloatingPanelTarget ? this.floatingPanelTarget : null
    this._floatingCounter = this.hasFloatingCounterTarget ? this.floatingCounterTarget : null

    if (this._floatingPanel) {
      document.body.appendChild(this._floatingPanel)
    }

    this.calculateSum()
    this.setupObserver()
  }

  disconnect() {
    if (this.observer) this.observer.disconnect()
    if (this._floatingPanel) this._floatingPanel.remove()
  }

  setupObserver() {
    if (!this.hasInlinePanelTarget || !this._floatingPanel) return

    this.observer = new IntersectionObserver(
      ([entry]) => {
        // Show floating panel once the inline panel scrolls out of view
        if (entry.isIntersecting) {
          this._floatingPanel.classList.add("hidden")
        } else {
          this._floatingPanel.classList.remove("hidden")
        }
      },
      { threshold: 0 }
    )

    this.observer.observe(this.inlinePanelTarget)
  }

  preventFractions(event) {
    if (event.key === '.' || event.key === ',') {
      event.preventDefault()
    }
  }

  inputChanged(event) {
    const input = event.currentTarget
    input.value = input.value.replace(/[^0-9]/g, '')
    let val = parseInt(input.value)
    if (isNaN(val)) val = 0
    if (val > 100) input.value = 100
    if (val < 0) input.value = 0
    this.calculateSum()
  }

  calculateSum() {
    let total = 0
    let allFilled = true

    this.inputTargets.forEach(input => {
      const val = parseInt(input.value)
      if (isNaN(val)) {
        allFilled = false
      } else {
        total += val
      }
    })

    const remaining = 100 - total

    // Color classes for each state
    const colorClass = remaining === 0 ? 'text-emerald-600'
                     : remaining < 0  ? 'text-red-600'
                     : 'text-blue-700'

    // Update inline counter (still in Stimulus scope)
    if (this.hasInlineCounterTarget) {
      this.inlineCounterTarget.textContent = remaining
      this.inlineCounterTarget.className = this.inlineCounterTarget.className
        .replace(/text-(blue|red|emerald)-\d+/g, '')
        .trim() + ` ${colorClass}`
    }

    // Update floating counter (stored ref — no longer a Stimulus target after teleport)
    if (this._floatingCounter) {
      this._floatingCounter.textContent = remaining
      this._floatingCounter.className = this._floatingCounter.className
        .replace(/text-(blue|red|emerald)-\d+/g, '')
        .trim() + ` ${colorClass}`
    }

    if (this.hasSubmitBtnTarget) {
      if (remaining === 0 && allFilled) {
        this.submitBtnTarget.disabled = false
        this.submitBtnTarget.classList.remove('opacity-50', 'cursor-not-allowed')
      } else {
        this.submitBtnTarget.disabled = true
        this.submitBtnTarget.classList.add('opacity-50', 'cursor-not-allowed')
      }
    }
  }
}
