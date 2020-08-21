<template>
  <div class="playlist">
    <div class="playlist-name" v-text="playlist.name" />
    <div class="playlist-options">
      <div @click="play" style="margin-right:2px" class="btn-rnd --c-b-green">Play</div>
      <div @click="delete_" class="btn-rnd --c-b-red">Delete</div>
    </div>
    <div style="font-size:120%;font-weight:bold;margin:20px 0px;">Songs</div>
    <a-list label="song" :data="playlist.songs" :current="current" />
  </div>
</template> 

<script>
import axios from 'axios'
import AList from '@/components/AList'

export default {
  components: {
    AList
  },
  data () {
    return {
      playlist: {},
      current: false
    }
  },
  methods: {
    play () {
      axios.post(`/api/play/playlist/${this.$route.params.id}`).then(
        () => console.log('playing playlist')
      )
    },
    delete_ () {
      axios.delete(`/api/playlist/${this.$route.params.id}`).then(
        () => console.log('deleted')
      )
    }
  },
  mounted () {
    let id = this.$route.params.id
    let s = this.$store.state
    if (s.playlistType === 'playlist' && s.playlistId === id) this.current = true
    axios.get(`/api/playlist/${id}`).then(res => this.playlist = res.data)
  }
}
</script>

<style>
.playlist {
  padding: 0px 20px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.playlist-options {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
}

.playlist-name {
  box-sizing: border-box;
  font-weight: bold;
  padding: 20px;
  text-align: center;
  width: 100%;
  font-size: 150%;
}
</style>