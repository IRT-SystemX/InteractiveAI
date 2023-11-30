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
    const component = document.getElementsByTagName('procedure-component')[0];
    component.hidden = false;
    // Get data for card clicked
    const res = await fetch('./shared/components/ProcedureView/procedure.json');
    const data = await res.json();

    let timeline = '';
    for (const block of data.procedure) {
      timeline += `<procedure-block><span slot="block">${block.blockText}</span></procedure-block>`;
      for (const task of block.tasks) {
        timeline += `<procedure-step><span slot="number">${task.taskIndex}</span><span slot="step">${task.taskText}</span></procedure-step>`;
      }
    }

    component.shadowRoot.querySelector('#procedure-component main').innerHTML = timeline;
  }

  showRecommendations(title) {
    getRecommandationDA(title);
  }
}

customElements.define('procedure-component', ProcedureComponent);
