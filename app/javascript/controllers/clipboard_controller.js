import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static values = { text: String }

  copy(event) {
    event.preventDefault()
    
    navigator.clipboard.writeText(this.textValue).then(() => {
      const svg = this.element.querySelector('svg')
      if (svg) {
        svg.classList.add('transition-colors', 'duration-300', 'text-emerald-500')
        
        setTimeout(() => {
          svg.classList.remove('text-emerald-500')
        }, 800)
      }
    }).catch(err => {
      console.error('Failed to copy text: ', err)
    })
  }
}
