class CorrelationRowComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    fetch('./shared/components/CorrelationView/CorrelationRow/template.html')
      .then((response) => response.text())
      .then((html) => {
        this.shadowRoot.innerHTML = html;
        this.shadowRoot.querySelector('.correlation-row').addEventListener('mouseenter', this.showLink.bind(this));
        this.shadowRoot.querySelector('.correlation-row').addEventListener('mouseleave', hideLink);
      })
      .catch((error) => console.error('Error fetching HTML:', error));
  }

  showLink() {
    showLink(+this.getAttribute('source'), +this.getAttribute('target'));
  }
}

customElements.define('correlation-row', CorrelationRowComponent);
