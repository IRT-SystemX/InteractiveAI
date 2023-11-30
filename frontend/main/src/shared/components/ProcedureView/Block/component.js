class ProcedureBlockComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    fetch('./shared/components/ProcedureView/Block/template.html')
      .then((response) => response.text())
      .then((html) => {
        this.shadowRoot.innerHTML = html;
      })
      .catch((error) => console.error('Error fetching HTML:', error));
  }
}

customElements.define('procedure-block', ProcedureBlockComponent);
