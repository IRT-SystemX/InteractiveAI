class CorrelationComponent extends HTMLElement {
  event;
  data;
  formatted;
  correlationSize;
  shown;
  size = 60;

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
        this.shadowRoot.getElementById('correlations-more').addEventListener('click', this.more.bind(this));
        this.shadowRoot.getElementById('refresh').addEventListener('click', () => this.getCorrelation(true));
      })
      .catch((error) => console.error('Error fetching HTML:', error));
  }

  async getCorrelation(reset) {
    if (reset) {
      this.shown = 5;
      this.event = AssistanceComponent.event;
      const res = await fetch(`${host}/cab_correlation/api/v1/correlation?size=${/*this.size*/ 1}&app_id=${this.event.card.data.metadata.id_app}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      this.data = await res.json();
      if (!this.data[0].data) {
        orange_ctx_container.innerHTML = 'Failed';
        return;
      }
    }
    this.formatted = this.formattedData(this.data[0].data);
    setCorrelation(this.formatted, this.event.card.data.metadata.id_app, this.shown, this.event.card.data.metadata.bad_kpi, this.event.card.severity);
    this.showCorrelations();
  }
  showCorrelations() {
    this.shadowRoot.getElementById('correlations').innerHTML = this.formatted
      .slice(0, this.shown)
      .map(
        ([key, value]) =>
          `<correlation-row source="${this.event.card.data.metadata.id_app}" target="${+/App_(\d+).*/.exec(
            key
          )[1]}"><div slot="app">App ${+/App_(\d+).*/.exec(key)[1]}</div><img slot="icon" title="${
            t(/App_\d+\.KPI(|_composite)\.(.*)/.exec(key)[2])
          }" src="./assets/images/kpi/${/App_\d+\.KPI(|_composite)\.(.*)/.exec(key)[2]}.svg"><div slot="correlation">${value.toFixed(
            0
          )}</div></correlation-row>`
      )
      .join('');
    this.shadowRoot.getElementById('number-correlations').innerText = this.formatted.length;
  }
  setSize(event) {
    this.size = 15; // event.target.value;
    this.shadowRoot.getElementById('size-value').innerText = `${this.size}min`;
    this.getCorrelation(true);
  }
  formattedData(data) {
    return Object.keys(data)
      .flatMap((key) => Object.entries(data[key]))
      .filter(([, value]) => value)
      .sort(([, a], [, b]) => b - a);
  }
  more() {
    this.shown += 5;
    this.getCorrelation(false);
  }
}

customElements.define('correlation-component', CorrelationComponent);