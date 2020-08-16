import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    currentSong: null,
    playing: false,
  },
  mutations: {
    currentSong (state, value) { state.currentSong = value },
    playing (state, value) { state.playing = value }
  }
})
