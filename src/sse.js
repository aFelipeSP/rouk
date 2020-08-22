import store from '@/store.js'
// import axios from 'axios'

function initSSE () {
    let source = new EventSource('/api/stream')
  
    source.addEventListener('update', function(e) {
      store.dispatch('updateState', e.data)
    }, false)

    source.addEventListener('close', function() {
      console.log('closing sse')
      source.close()
    }, false)
  
    // eslint-disable-next-line no-unused-vars
    source.addEventListener('error', function() {
      source.close()
    }, false)
  
    return source
  }
  
  export { initSSE }