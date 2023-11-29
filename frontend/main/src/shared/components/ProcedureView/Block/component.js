class ProcedureBlockComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    fetch('./shared/components/ProcedureView/Block/template.html')
      .then((response) => response.text())
      .then((html) => {
        this.shadowRoot.innerHTML = html;
        this.addEventListener('mouseenter', this.showLink.bind(this));
        this.addEventListener('mouseleave', hideLink);
        this.addEventListener('click', () => this.setAttribute('style', 'filter:grayscale(1)'));
      })
      .catch((error) => console.error('Error fetching HTML:', error));
  }

  showLink() {
    showLink(+this.getAttribute('source'), +this.getAttribute('target'));
  }
}

customElements.define('procedure-block', ProcedureBlockComponent);
