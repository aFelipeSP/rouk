module.exports = {
  productionSourceMap: process.env.NODE_ENV !== 'production',
  publicPath: process.env.NODE_ENV === 'production' ? '/static/' : '/',
  outputDir: 'rouk/static'
}