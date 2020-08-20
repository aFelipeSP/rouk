import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    playlistType: null,
    playlistId: null,
    song: null,
    track: null,
    time: null,
    playing: false,
    random: false,
    searchLabel: 'playlist',
    searchValue: null,
    loading: false,
    update: false
  },
  mutations: {
    playlistType (state, value) { state.playlistType = value },
    playlistId (state, value) { state.playlistId = value },
    song (state, value) { state.song = value },
    track (state, value) { state.track = value },
    time (state, value) { state.time = value },
    playing (state, value) { state.playing = value },
    random (state, value) { state.random = value },
    searchLabel (state, value) { state.searchLabel = value },
    searchValue (state, value) { state.searchValue = value },
    loading (state, value) { state.loading = value },
    update (state, value) { state.update = value }
  }
})
