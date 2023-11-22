class CorrelationComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    fetch('./shared/components/CorrelationView/template.html')
      .then((response) => response.text())
      .then((html) => {
        // Injecter le HTML dans le shadow DOM
        this.shadowRoot.innerHTML = html;

        // Add event listener for the correlate button
        const correlationSize = this.shadowRoot.getElementById('correlation-size');
        correlationSize.addEventListener('change', this.setSize.bind(this));
      })
      .catch((error) => console.error('Error fetching HTML:', error));
  }

  setSize() {
    // Implement the correlate functionality here
    console.log('setSize');
  }
}

customElements.define('correlation-component', CorrelationComponent);
