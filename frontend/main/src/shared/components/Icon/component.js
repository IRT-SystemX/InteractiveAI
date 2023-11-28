class AssistanceComponent extends HTMLElement {
  static event;
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
    this.hidden = true;
    document.getElementsByTagName('correlation-component')[0].hidden = false;
    document.getElementsByTagName('correlation-component')[0].getCorrelation(true);
  }

  static async showAssistanceView(id) {
    document.getElementsByTagName('correlation-component')[0].hidden = true;
    document.getElementsByTagName('assistance-component')[0].hidden = false;
    // Get data for card clicked
    const res = await fetch(`${host}/cards/cards/${id}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    this.event = await res.json();
    showNode(+this.event.card.data.metadata.id_app)
    document.getElementsByTagName('assistance-component')[0].shadowRoot.getElementById('app-id').innerText = +this.event.card.data.metadata.id_app;
  }
}

customElements.define('assistance-component', AssistanceComponent);
