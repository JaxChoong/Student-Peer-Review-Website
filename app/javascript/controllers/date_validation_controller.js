import { Controller } from "@hotwired/stimulus"

// Sets dynamic min/max bounds on start and end dates.
// Usage:
//   data-controller="date-validation"
//   data-date-validation-target="startDate"  (on start date input)
//   data-date-validation-target="endDate"    (on end date input)
export default class extends Controller {
  static targets = ["startDate", "endDate"]

  connect() {
    this.validate()
  }

  validate() {
    if (!this.hasStartDateTarget || !this.hasEndDateTarget) return

    const start = this.startDateTarget.value
    const end   = this.endDateTarget.value

    if (start) {
      // End date must be strictly after start date
      const startDate = new Date(start)
      if (!isNaN(startDate)) {
        startDate.setUTCDate(startDate.getUTCDate() + 1)
        this.endDateTarget.min = startDate.toISOString().split("T")[0]
      }
    } else {
      this.endDateTarget.min = ""
    }

    if (end) {
      // Start date must be strictly before end date
      const endDate = new Date(end)
      if (!isNaN(endDate)) {
        endDate.setUTCDate(endDate.getUTCDate() - 1)
        this.startDateTarget.max = endDate.toISOString().split("T")[0]
      }
    } else {
      this.startDateTarget.max = ""
    }
  }
}
