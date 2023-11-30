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

  static async showProcedureView() {
    const component = document.getElementsByTagName('procedure-component')[0];
    component.hidden = false;
    // Get data for card clicked
    const res = await fetch(`${host}/cab_recommendation/api/v1/procedure`, {
      method: 'POST',
      body: JSON.stringify({
        event: {
          event_type: 'ENG1: AUTO SHUTDOWN',
        },
      }),
      headers: {
        "Content-Type": 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    const data = await res.json();

    let timeline = '';
    let index = 0;
    for (const block of data.procedure) {
      timeline += `<procedure-block><span slot="block">${block.blockText}</span></procedure-block>`;
      for (const task of block.tasks) {
        timeline += `<procedure-step step="${index}" ${task.taskText.match(/land asap/gi) ? 'landing' : ''} state="${
          !index ? 'doing' : 'todo'
        }"><span slot="number">${task.taskIndex}</span><span slot="step">${task.taskText}</span></procedure-step>`;
        index++;
      }
    }

    component.shadowRoot.querySelector('#procedure-component main').innerHTML = timeline;
  }
}

customElements.define('procedure-component', ProcedureComponent);
