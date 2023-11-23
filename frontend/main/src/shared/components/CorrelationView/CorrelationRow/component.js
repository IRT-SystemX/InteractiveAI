class CorrelationRowComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    fetch('./shared/components/CorrelationView/CorrelationRow/template.html')
      .then((response) => response.text())
      .then((html) => {
        this.shadowRoot.innerHTML = html;
      })
      .catch((error) => console.error('Error fetching HTML:', error));
  }
}

customElements.define('correlation-row', CorrelationRowComponent);
