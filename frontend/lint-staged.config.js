export default {
  '*.{vue,ts,js,jsx,cjs,mjs,tsx,cts,mts}': ['eslint --fix', 'prettier --write'],
  '*.{css,scss,json,html,yml,md}': 'prettier --write',
  '*.svg': 'svgo --multipass'
}
