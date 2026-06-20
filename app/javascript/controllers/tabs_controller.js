import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["btn", "pane"]
  static classes = ["activeTab", "inactiveTab", "hidden"]

  connect() {
    // If no tab is active, activate the first one
    if (this.btnTargets.length > 0) {
      const activeBtn = this.btnTargets.find(btn => btn.classList.contains(this.activeTabClasses[0]))
      if (!activeBtn) {
        this.switch({ currentTarget: this.btnTargets[0] })
      }
    }
  }

  switch(event) {
    if (event.preventDefault) {
      event.preventDefault()
    }
    
    const clickedBtn = event.currentTarget
    const targetId = clickedBtn.dataset.targetId
    
    // Deactivate all buttons
    this.btnTargets.forEach(btn => {
      btn.classList.remove(...this.activeTabClasses)
      btn.classList.add(...this.inactiveTabClasses)
    })
    
    // Activate clicked button
    clickedBtn.classList.add(...this.activeTabClasses)
    clickedBtn.classList.remove(...this.inactiveTabClasses)
    
    // Hide all panes, show target
    this.paneTargets.forEach(pane => {
      pane.classList.add(...this.hiddenClasses)
      if (pane.id === targetId) {
        pane.classList.remove(...this.hiddenClasses)
      }
    })
  }
}
