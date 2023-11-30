class ProcedureStepComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    fetch('./shared/components/ProcedureView/Step/template.html')
      .then((response) => response.text())
      .then((html) => {
        this.shadowRoot.innerHTML = html;
        this.addEventListener('click', () => this.setAttribute('state', 'done'));
      })
      .catch((error) => console.error('Error fetching HTML:', error));
  }
}

customElements.define('procedure-step', ProcedureStepComponent);
