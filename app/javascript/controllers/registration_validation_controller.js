import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["pwd", "pwdConf", "lengthItem", "lengthIcon", "matchItem", "matchIcon"]

  connect() {
    if (this.hasPwdTarget && this.hasPwdConfTarget) {
      this.updateCriteria()
    }
  }

  updateCriteria() {
    const pVal = this.pwdTarget.value
    const pcVal = this.pwdConfTarget.value

    const checkSvg = `<path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />`
    const crossSvg = `<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />`

    // 1. Length check
    if (pVal.length >= 6) {
      this.lengthItemTarget.className = "flex items-center gap-1.5 text-xs text-emerald-600 font-semibold"
      this.lengthIconTarget.innerHTML = checkSvg
      this.lengthIconTarget.className = "h-4 w-4 text-emerald-500 shrink-0"
    } else {
      this.lengthItemTarget.className = "flex items-center gap-1.5 text-xs text-slate-500 font-medium"
      this.lengthIconTarget.innerHTML = crossSvg
      this.lengthIconTarget.className = "h-4 w-4 text-slate-400 shrink-0"
    }

    // 2. Match check
    if (pVal.length > 0 && pVal === pcVal) {
      this.matchItemTarget.className = "flex items-center gap-1.5 text-xs text-emerald-600 font-semibold"
      this.matchIconTarget.innerHTML = checkSvg
      this.matchIconTarget.className = "h-4 w-4 text-emerald-500 shrink-0"
    } else {
      this.matchItemTarget.className = "flex items-center gap-1.5 text-xs text-slate-500 font-medium"
      this.matchIconTarget.innerHTML = crossSvg
      this.matchIconTarget.className = "h-4 w-4 text-slate-400 shrink-0"
    }
  }
}
