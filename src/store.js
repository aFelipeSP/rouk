import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    currentLabel: null,
    currentPlaylist: null,
    currentSong: null,
    playing: false,
    searchLabel: 'playlist',
    searchValue: null

  },
  mutations: {
    currentLabel (state, value) { state.currentLabel = value },
    currentPlaylist (state, value) { state.currentPlaylist = value },
    currentSong (state, value) { state.currentSong = value },
    playing (state, value) { state.playing = value },
    searchLabel (state, value) { state.searchLabel = value },
    searchValue (state, value) { state.searchValue = value }
  }
})
