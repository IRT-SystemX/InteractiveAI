class AssistanceComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    fetch('./shared/components/AssistanceView/template.html')
      .then((response) => response.text())
      .then((html) => {
        // Injecter le HTML dans le shadow DOM
        this.shadowRoot.innerHTML = html;

        // Ajouter un gestionnaire d'événement pour le bouton correlate
        const correlateBtn = this.shadowRoot.getElementById('correlateBtn');
        correlateBtn.addEventListener('click', this.correlate.bind(this));
      })
      .catch((error) => console.error('Error fetching HTML:', error));
  }

  correlate() {
    // Implement the correlate functionality here
    this.hidden = true;
    document.getElementsByTagName('correlation-component')[0].hidden = false;
  }
}

customElements.define('assistance-component', AssistanceComponent);
