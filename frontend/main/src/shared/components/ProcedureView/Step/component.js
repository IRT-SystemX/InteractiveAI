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
    document.getElementsByTagName('procedure-component')[0].hidden = true;
    var recoResponse;
    var data = JSON.stringify({
      event: {
        event_type: title,
      },
    });
    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;
    xhr.addEventListener('readystatechange', function () {
      if (this.readyState === 4) {
        document.getElementById('da_block_request').innerHTML = '';
        document.getElementById('da_block_request').innerHTML += 'Procedure <hr>';
        recoResponse = JSON.parse(this.responseText);
        Object.keys(recoResponse).forEach(function (k) {
          document.getElementById('da_block_request').hidden = false;
          document.getElementById('da_block_request').innerHTML += recoResponse[k].title + '<hr>';
        });
      }
    });
    xhr.open('POST', host + '/cab_recommendation/api/v1/recommendation');
    xhr.setRequestHeader('Authorization', 'Bearer ' + window.localStorage.token);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(data);
  }
}

customElements.define('procedure-step', ProcedureStepComponent);
