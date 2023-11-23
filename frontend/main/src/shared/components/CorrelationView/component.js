class CorrelationComponent extends HTMLElement {
  event;
  data;
  correlationSize;
  size = 1;

  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    fetch('./shared/components/CorrelationView/template.html')
      .then((response) => response.text())
      .then((html) => {
        // Injecter le HTML dans le shadow DOM
        this.shadowRoot.innerHTML = html;

        // Add event listener for the correlate button
        this.correlationSize = this.shadowRoot.getElementById('correlation-size');
        this.correlationSize.addEventListener('change', this.setSize.bind(this));
        this.correlationSize.value = this.size;
      })
      .catch((error) => console.error('Error fetching HTML:', error));
  }

  async getCorrelation() {
    this.event = AssistanceComponent.event;
    const res = await fetch(
      `${host}/cab_correlation/api/v1/correlation?size=${this.size}&app_id=${this.event.card.data.metadata.id_app}&kpi_name=${this.event.card.data.metadata.bad_kpi}`,
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      }
    );
    this.data = await res.json();
    if (!this.data[0].data) {
      orange_ctx_container.innerHTML = 'Failed';
      return;
    }
    setCorrelation(
      this.data[0].data,
      this.event.card.data.metadata.id_app,
      this.event.card.data.metadata.bad_kpi,
      this.event.card.severity
    );
  }
  setSize(event) {
    this.size = event.target.value;
    this.getCorrelation();
  }
}

customElements.define('correlation-component', CorrelationComponent);
