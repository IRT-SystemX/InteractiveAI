# ![](/public/favicon-32x32.png) CAB Front

Commits use [conventional commit](https://www.conventionalcommits.org/en/v1.0.0/#summary) specification.  
You can easily compose your commit message using `npm run commit`.

## Packages used

- **[Vue](https://vuejs.org/guide/introduction.html)**
- [Vue router](https://router.vuejs.org/guide/) for routing
- [Axios](https://axios-http.com/docs/intro) for networking
- [Pinia](https://pinia.vuejs.org/core-concepts/) for store
- [Mitt](https://github.com/developit/mitt) for event hub
- [D3](https://d3js.org/getting-started) for data visualisation
- [Leaflet](https://leafletjs.com/reference.html) for maps
- [Lucide](https://lucide.dev/icons/) for icons
- [date-fns](https://date-fns.org/docs/Getting-Started) for date formatting
- [Vue I18n](https://vue-i18n.intlify.dev/) for internationalization

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur) + [TypeScript Vue Plugin (Volar)](https://marketplace.visualstudio.com/items?itemName=Vue.vscode-typescript-vue-plugin).

## Type Support for `.vue` Imports in TS

TypeScript cannot handle type information for `.vue` imports by default, so we replace the `tsc` CLI with `vue-tsc` for type checking. In editors, we need [TypeScript Vue Plugin (Volar)](https://marketplace.visualstudio.com/items?itemName=Vue.vscode-typescript-vue-plugin) to make the TypeScript language service aware of `.vue` types.

If the standalone TypeScript plugin doesn't feel fast enough to you, Volar has also implemented a [Take Over Mode](https://github.com/johnsoncodehk/volar/discussions/471#discussioncomment-1361669) that is more performant. You can enable it by the following steps:

1. Disable the built-in TypeScript Extension
   1. Run `Extensions: Show Built-in Extensions` from VSCode's command palette
   2. Find `TypeScript and JavaScript Language Features`, right click and select `Disable (Workspace)`
2. Reload the VSCode window by running `Developer: Reload Window` from the command palette.

## Customize configuration

See [Vite Configuration Reference](https://vitejs.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
npm run dev: {mode} # run dev environment where {mode} is
                    # demo, development, prod, production, simu
```

### Type-Check, Compile and Minify for Production

```sh
npm run build
npm run build: {mode} # build specific environment where {mode} is
                    # demo, development, prod, production, simu
```

### Run Unit Tests with [Vitest](https://vitest.dev/)

```sh
npm run test:unit
```

### Run End-to-End Tests with [Cypress](https://www.cypress.io/)

```sh
npm run test:e2e:dev
```

This runs the end-to-end tests against the Vite development server.
It is much faster than the production build.

But it's still recommended to test the production build with `test:e2e` before deploying (e.g. in CI environments):

```sh
npm run build
npm run test:e2e
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```
