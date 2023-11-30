class ProcedureStepComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    fetch('./shared/components/ProcedureView/Step/template.html')
      .then((response) => response.text())
      .then((html) => {
        this.shadowRoot.innerHTML = html;
        this.addEventListener('click', () => this.nextStep());
        this.shadowRoot.getElementById('procedure-step-landing').addEventListener('click', () => this.getRecommandationDA('test'));
      })
      .catch((error) => console.error('Error fetching HTML:', error));
  }

  nextStep() {
    if (this.getAttribute('state') === 'doing') {
      this.setAttribute('state', 'done');
      document
        .getElementsByTagName('procedure-component')[0]
        .shadowRoot.querySelector(`procedure-step[step="${+this.getAttribute('step') + 1}"]`)
        .setAttribute('state', 'doing');
    }
  }

  getRecommandationDA(title) {
    this.setAttribute('state', 'done');
    document.getElementsByTagName('procedure-component')[0].hidden = true;
    askRecoDA();
  }
}

customElements.define('procedure-step', ProcedureStepComponent);
