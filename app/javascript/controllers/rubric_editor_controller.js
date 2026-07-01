import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["criteriaContainer", "criteriaTemplate", "columnTemplate", "form", "nameInput"]

  connect() {
    // If no criteria rows exist, add one
    if (this.criteriaContainerTarget.children.length === 0) {
      this.addCriteria()
    }
    this.initMarkdownPreviews(this.criteriaContainerTarget)
  }

  addCriteria(event) {
    if (event) event.preventDefault()

    const clone = this.criteriaTemplateTarget.content.cloneNode(true)
    const row = clone.querySelector('.criteria-row')
    const colsContainer = row.querySelector('.columns-container')
    
    // Auto-add 4 columns to the new row
    for (let i = 0; i <= 3; i++) {
      this.insertColumn(colsContainer, i)
    }

    this.criteriaContainerTarget.appendChild(clone)
    // Wire previews for the newly added row
    const addedRow = this.criteriaContainerTarget.lastElementChild
    this.initMarkdownPreviews(addedRow)
  }

  removeCriteria(event) {
    event.preventDefault()
    const row = event.currentTarget.closest('.criteria-row')
    
    if (this.criteriaContainerTarget.querySelectorAll('.criteria-row').length > 1) {
      row.remove()
    } else {
      alert("You must have at least one criteria row.")
    }
  }

  addColumn(event) {
    event.preventDefault()
    const row = event.currentTarget.closest('.criteria-row')
    const container = row.querySelector('.columns-container')
    const currentCount = container.querySelectorAll('.column-card').length
    
    if (currentCount >= 10) {
      alert("Maximum 10 columns allowed per criteria.")
      return
    }
    
    this.insertColumn(container)
    // Wire preview for the newly added column
    const addedCol = container.lastElementChild
    this.wireMarkdownPreview(addedCol)
  }

  insertColumn(container, weightValue) {
    const colClone = this.columnTemplateTarget.content.cloneNode(true)
    
    if (weightValue !== undefined) {
      colClone.querySelector('.col-weight-input').value = weightValue
    }
    
    container.appendChild(colClone)
  }

  removeColumn(event) {
    event.preventDefault()
    const card = event.currentTarget.closest('.column-card')
    const container = card.closest('.columns-container')
    
    if (container.querySelectorAll('.column-card').length > 1) {
      card.remove()
    } else {
      alert("You must have at least one column.")
    }
  }

  // ── Markdown Helpers ─────────────────────────────────────

  // Wire up all column cards within a container/row
  initMarkdownPreviews(container) {
    container.querySelectorAll('.column-card').forEach(card => this.wireMarkdownPreview(card))
  }

  // Wire write/preview tabs and live render for a single column card
  wireMarkdownPreview(card) {
    const textarea = card.querySelector('.col-desc-input')
    const preview  = card.querySelector('.col-desc-preview')
    const writeBtn = card.querySelector('.col-write-tab')
    const prevBtn  = card.querySelector('.col-preview-tab')
    if (!textarea || !preview || !writeBtn || !prevBtn) return

    const render = () => {
      const raw = textarea.value
      preview.innerHTML = raw
        ? (typeof marked !== 'undefined' ? marked.parse(raw) : raw)
        : '<p class="text-slate-400 italic text-xs">Nothing to preview.</p>'
    }

    writeBtn.addEventListener('click', (e) => {
      e.preventDefault()
      textarea.classList.remove('hidden')
      preview.classList.add('hidden')
      writeBtn.classList.add('bg-white', 'text-blue-600', 'shadow-sm')
      writeBtn.classList.remove('text-slate-500')
      prevBtn.classList.remove('bg-white', 'text-blue-600', 'shadow-sm')
      prevBtn.classList.add('text-slate-500')
    })

    prevBtn.addEventListener('click', (e) => {
      e.preventDefault()
      render()
      textarea.classList.add('hidden')
      preview.classList.remove('hidden')
      prevBtn.classList.add('bg-white', 'text-blue-600', 'shadow-sm')
      prevBtn.classList.remove('text-slate-500')
      writeBtn.classList.remove('bg-white', 'text-blue-600', 'shadow-sm')
      writeBtn.classList.add('text-slate-500')
    })
  }

  save(event) {
    event.preventDefault()
    
    const form = this.formTarget
    
    // Remove existing hidden inputs
    form.querySelectorAll('.generated-hidden-input').forEach(el => el.remove())
    
    let isValid = true
    const rows = this.criteriaContainerTarget.querySelectorAll('.criteria-row')
    
    rows.forEach((row, criteriaIndex) => {
      const labelInput = row.querySelector('.criteria-label-input')
      const label = labelInput.value.trim()
      
      if (!label) {
        isValid = false
        labelInput.classList.add('border-rose-500')
      } else {
        labelInput.classList.remove('border-rose-500')
      }
      
      this.appendHiddenInput(form, `rubric_template[criteria][${criteriaIndex}][label]`, label)
      this.appendHiddenInput(form, `rubric_template[criteria][${criteriaIndex}][position]`, criteriaIndex)
      
      const columns = row.querySelectorAll('.column-card')
      columns.forEach((col, colIndex) => {
        const weightInput = col.querySelector('.col-weight-input')
        const weight = weightInput.value
        
        if (weight === "") {
          isValid = false
          weightInput.classList.add('border-rose-500')
        } else {
          weightInput.classList.remove('border-rose-500')
        }
        
        const descriptions = col.querySelector('.col-desc-input').value
        
        this.appendHiddenInput(form, `rubric_template[criteria][${criteriaIndex}][columns][${colIndex}][weight]`, weight)
        this.appendHiddenInput(form, `rubric_template[criteria][${criteriaIndex}][columns][${colIndex}][position]`, colIndex)
        this.appendHiddenInput(form, `rubric_template[criteria][${criteriaIndex}][columns][${colIndex}][descriptions]`, descriptions)
      })
    })
    
    if (!this.nameInputTarget.value.trim()) {
      this.nameInputTarget.reportValidity()
      return
    }
    
    if (isValid) {
      form.submit()
    } else {
      alert("Please fill in all required fields (Criteria labels and Column weights).")
    }
  }
  
  appendHiddenInput(form, name, value) {
    const input = document.createElement('input')
    input.type = 'hidden'
    input.name = name
    input.value = value
    input.classList.add('generated-hidden-input')
    form.appendChild(input)
  }
}
