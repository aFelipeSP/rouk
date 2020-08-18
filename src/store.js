import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    currentLabel: null,
    currentPlaylist: null,
    currentSong: null,
    playing: false,
  },
  mutations: {
    currentLabel (state, value) { state.currentLabel = value },
    currentPlaylist (state, value) { state.currentPlaylist = value },
    currentSong (state, value) { state.currentSong = value },
    playing (state, value) { state.playing = value }
  }
})
