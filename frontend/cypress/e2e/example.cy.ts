// https://on.cypress.io/api

describe('Check login button', () => {
  it('visits the app root url', () => {
    cy.visit('/')
    cy.contains('button', 'Log in')
  })
})
