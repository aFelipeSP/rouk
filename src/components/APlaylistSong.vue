<template>
  <div class="playlist-song">
    <a-search-bar v-model="searchValue" />
    <div
      v-for="(playlist, i) in playlists"
      :key="i"
      class="playlist-song-item"
      @click="select(playlist)"
    >
      {{playlist.name}}
    </div>
  </div>
</template>


<script>
import ASearchBar from '@/components/ASearchBar'
import axios from 'axios'

export default {
  components: {
    ASearchBar
  },
  props: {
    song: Number
  },
  data () {
    return {
      searchValue: null,
      playlists: []
    }
  },
  methods: {
    search () {
      axios.get(`/api/playlist?q=${this.searchValue || ''}`).then(
        a => {this.playlists = a.data}
      )
    },
    select (playlist) {
      axios.put(`/api/playlist/${playlist}`, {songs: [this.song]}).then(
        () => console.log('song_added')
      )
    }
  },
  watch: {
    searchValue: {
      handler () {
        this.search()
      },
      immediate: true
    }
  },
  mounted () {
    this.search()
  }
}
</script>

<style>
.playlist-song-item {
  padding: 10px;
}
</style>