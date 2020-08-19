import store from '@/store.js'
import axios from 'axios'

function initSSE () {
    let source = new EventSource(axios.defaults.baseURL + 'api/stream')
  
    source.addEventListener('update', function(e) {
      let data = JSON.parse(e.data)
      for (let prop in data) {
        store.commit(prop, data[prop])
      }
    }, false)
  
    // eslint-disable-next-line no-unused-vars
    source.addEventListener('error', function(err) {
      // pass
    }, false)
  
    return source
  }
  
  export { initSSE }