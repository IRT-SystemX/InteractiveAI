class CorrelationComponent extends HTMLElement {
  event;
  data;
  shownData;
  correlationSize;
  shown = 6;
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
        this.shadowRoot.getElementById('correlations-more').addEventListener('click', this.more.bind(this));
      })
      .catch((error) => console.error('Error fetching HTML:', error));
  }

  async getCorrelation(reset) {
    if (reset) this.shown = 6;
    this.event = AssistanceComponent.event;
    const res = await fetch(
      `${host}/cab_correlation/api/v1/correlation?size=${this.size}&app_id=${this.event.card.data.metadata.id_app}`,
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
    this.shownData = this.indexThreshold(this.data[0].data);
    setCorrelation(this.shownData, this.event.card.data.metadata.id_app, this.event.card.data.metadata.bad_kpi, this.event.card.severity);
    this.showCorrelations();
  }
  showCorrelations() {
    const obj =
      this.shownData[
        `App_${AssistanceComponent.event.card.data.metadata.id_app.padStart('2', '0')}.KPI.${AssistanceComponent.event.card.data.metadata.bad_kpi}`
      ];
    this.shadowRoot.getElementById('correlations').innerHTML = Object.keys(obj)
      .map(
        (key) =>
          `<correlation-row><div slot="app">App ${+/App_(\d+).*/.exec(key)[1]}</div><img slot="icon" src="./assets/images/kpi/${
            /App_\d+\.KPI\.(.*)/.exec(key)[1]
          }.svg"><div slot="correlation">${(+obj[key]).toFixed(0)}</div></correlation-row>`
      )
      .join('');
  }
  setSize(event) {
    //this.size = event.target.value;
    this.getCorrelation();
  }
  indexThreshold(data) {
    return {
      [`App_${AssistanceComponent.event.card.data.metadata.id_app.padStart('2', '0')}.KPI.${AssistanceComponent.event.card.data.metadata.bad_kpi}`]:
        Object.entries(
          data[
            `App_${AssistanceComponent.event.card.data.metadata.id_app.padStart('2', '0')}.KPI.${
              AssistanceComponent.event.card.data.metadata.bad_kpi
            }`
          ]
        )
          .sort(([, a], [, b]) => b - a)
          .slice(0, this.shown)
          .reduce((r, [k, v]) => ({ ...r, [k]: v }), {}),
    };
  }
  more() {
    console.debug('more!!!');
    this.shown += 6;
    this.getCorrelation();
  }
}

customElements.define('correlation-component', CorrelationComponent);
