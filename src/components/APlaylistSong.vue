<template>
  <div class="playlist-song">
    <a-search-bar v-model="searchValue" style="background-color: transparent;"/>
    <div class="playlist-song-item --add" @click="newPlaylist">
      <icon-plus style="width:1em;margin-right:0.6em" /><div>New playlist</div>
    </div>
    <div
      v-for="(playlist, i) in playlists"
      :key="i"
      class="playlist-song-item"
      @click="select(playlist.id)"
    >
      {{playlist.name}}
    </div>
  </div>
</template>


<script>
import ASearchBar from '@/components/ASearchBar'
import IconPlus from '@/icons/plus'
import axios from 'axios'

export default {
  components: {
    ASearchBar,
    IconPlus
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
    select (id_) {
      axios.put(`/api/playlist/${id_}`, {songs: [this.song]}).then(
        () => console.log('song_added')
      )
    },
    newPlaylist () {
      if (![null, ''].includes(this.searchValue)) {
        axios.post(
          '/api/playlist',
          { name: this.searchValue, songs: [this.song] }
        ).then(
          () => console.log('song_added')
        )
      }
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
  border-top: 1px solid #dddddd;
  cursor: pointer;
}

.playlist-song-item:hover {
  background-color: #dddddd;
}

.playlist-song-item.--add {
  display: flex;
  align-items: center;
  justify-content: center;
}

</style>