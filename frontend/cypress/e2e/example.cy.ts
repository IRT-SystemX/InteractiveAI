// https://on.cypress.io/api

describe('Check login button', () => {
  it('visits the app root url', () => {
    cy.visit('/')
    cy.get('input[type="text"]').type('admin')
    cy.get('input[type="password"]').type('test')
    cy.contains('button', 'Log in').click()
  })
})
