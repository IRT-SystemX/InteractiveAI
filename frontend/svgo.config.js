module.exports = {
  multipass: true,
  plugins: [
    'preset-default',
    'removeDimensions',
    {
      name: 'addAttributesToSVGElement',
      params: {
        attributes: [{ id: 'root' }]
      }
    }
  ]
}
