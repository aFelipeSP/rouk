import store from '@/store.js'
import axios from 'axios'

function initSSE () {
    let source = new EventSource(axios.defaults.baseURL + 'api/stream')
  
    source.addEventListener('t', function(e) {
      console.log(e.data)
    }, false)
    source.addEventListener('m', function(e) {
      console.log(e.data)
    }, false)
    source.addEventListener('a', function(e) {
      console.log(e.data)
    }, false)
    source.addEventListener('e', function(e) {
      console.log(e.data)
    }, false)
    source.addEventListener('s', function(e) {
      console.log(e.data)
    }, false)
    source.addEventListener('p', function() {
      store.commit('playing', true)
    }, false)
    source.addEventListener('n', function(e) {
      console.log(e.data)
    }, false)
    source.addEventListener('l', function(e) {
      console.log(e.data)
    }, false)
    source.addEventListener('r', function(e) {
      console.log(e.data)
    }, false)  
  
    // eslint-disable-next-line no-unused-vars
    source.addEventListener('error', function(err) {
      // pass
    }, false)
  
    return source
  }
  
  export { initSSE }