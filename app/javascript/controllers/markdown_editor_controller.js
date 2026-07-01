import { Controller } from "@hotwired/stimulus"

// Generic markdown editor with Write / Preview tabs.
// Usage:
//   data-controller="markdown-editor"
//   data-markdown-editor-target="textarea"    (the <textarea>)
//   data-markdown-editor-target="preview"     (the rendered preview div)
//   data-markdown-editor-target="writeTab"    (Write tab button)
//   data-markdown-editor-target="previewTab"  (Preview tab button)
export default class extends Controller {
  static targets = ["textarea", "preview", "writeTab", "previewTab"]

  connect() {
    this.showWrite()
  }

  showWrite() {
    this.textareaTarget.classList.remove("hidden")
    this.previewTarget.classList.add("hidden")
    this.writeTabTarget.classList.add("border-blue-500", "text-blue-600")
    this.writeTabTarget.classList.remove("border-transparent", "text-slate-500")
    this.previewTabTarget.classList.remove("border-blue-500", "text-blue-600")
    this.previewTabTarget.classList.add("border-transparent", "text-slate-500")
  }

  showPreview() {
    const raw = this.textareaTarget.value
    this.previewTarget.innerHTML = raw ? marked.parse(raw) : "<p class=\"text-slate-400 italic text-sm\">Nothing to preview yet.</p>"
    this.previewTarget.classList.remove("hidden")
    this.textareaTarget.classList.add("hidden")
    this.previewTabTarget.classList.add("border-blue-500", "text-blue-600")
    this.previewTabTarget.classList.remove("border-transparent", "text-slate-500")
    this.writeTabTarget.classList.remove("border-blue-500", "text-blue-600")
    this.writeTabTarget.classList.add("border-transparent", "text-slate-500")
  }
}
