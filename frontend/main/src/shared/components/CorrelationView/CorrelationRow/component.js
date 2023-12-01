class CorrelationRowComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    fetch('./shared/components/CorrelationView/CorrelationRow/template.html')
      .then((response) => response.text())
      .then((html) => {
        this.shadowRoot.innerHTML = html;
        this.addEventListener('mouseenter', this.showLink.bind(this));
        this.addEventListener('mouseleave', hideLink);
        this.addEventListener('click', this.focusLink.bind(this));
      })
      .catch((error) => console.error('Error fetching HTML:', error));
  }

  showLink() {
    showLink(+this.getAttribute('source'), +this.getAttribute('target'));
  }
  focusLink(){
    this.classList.add('clicked')
    focusLink(+this.getAttribute('source'), +this.getAttribute('target'));
  }
}

customElements.define('correlation-row', CorrelationRowComponent);
