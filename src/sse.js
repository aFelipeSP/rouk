import store from '@/store.js'
import axios from 'axios'


function setState (d) {
  if (d.label) store.commit('currentLabel', d.label)
  if (d.id) store.commit('currentPlaylist', d.id)
  if (d.song) store.commit('currentSong', d.song)
  if (d.playing) store.commit('playing', d.playing)
}

function play (label, data) {
  let d = JSON.parse(data)
  setState({label, id: d.id, song: d.song, playing: true})
}

function initSSE () {
    let source = new EventSource(axios.defaults.baseURL + 'api/stream')
  
    source.addEventListener('t', function(e) {
      console.log(e.data)
      play('playlist', e.data)
    }, false)
    source.addEventListener('m', function(e) {
      console.log(e.data)
      play('album', e.data)
    }, false)
    source.addEventListener('a', function(e) {
      console.log(e.data)
      play('artist', e.data)
    }, false)
    source.addEventListener('e', function(e) {
      console.log(e.data)
      setState({song: null, playing: false})
    }, false)
    source.addEventListener('s', function(e) {
      console.log(e.data)
      setState({song: e.data.song, playing: true})
    }, false)
    source.addEventListener('p', function(e) {
      store.commit('playing', e.data == '1' ? true : false)
    }, false)
    source.addEventListener('n', function(e) {
      console.log(e.data)
      play('playlist', e.data)
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