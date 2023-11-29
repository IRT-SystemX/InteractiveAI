class ProcedureComponent extends HTMLElement {
  static event;
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    fetch('./shared/components/ProcedureView/template.html')
      .then((response) => response.text())
      .then(async (html) => {
        // Injecter le HTML dans le shadow DOM
        this.shadowRoot.innerHTML = html;
      })
      .catch((error) => console.error('Error fetching HTML:', error));
  }

  static async showProcedureView(id) {
    document.getElementsByTagName('procedure-component')[0].hidden = false;
    // Get data for card clicked
    const res = await fetch('./shared/components/ProcedureView/procedure.json');
    const data = await res.json();
    for (const block of data.procedure) {
      console.debug(block);
    }
  }

  showRecommendations(title) {
    getRecommandationDA(title);
  }
}

customElements.define('procedure-component', ProcedureComponent);
