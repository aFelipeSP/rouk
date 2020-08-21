<template>
  <div class="album">
    <div class="album-name" v-text="album.name" />
    <div class="album-artist" @click="goToArtist">
      By {{(album.artist || {}).name}}
    </div>
    <div class="album-options">
      <div @click="play" class="btn-rnd --c-b-green">Play</div>
    </div>
    <div style="font-size:120%;font-weight:bold;margin:20px 0px;">Songs</div>
    <a-list label="song" :data="album.songs" :current="current" />
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
      album: {},
      current: false
    }
  },
  methods: {
    play () {
      axios.post(`/api/play/album/${this.$route.params.id}`).then(
        () => console.log('playing album')
      )
    },
    goToArtist () {
      this.$router.push(
        { name: 'artist', params: { id: this.album.artist.id } }
      ).catch(()=>{})
    }
  },
  mounted () {
    let id = this.$route.params.id
    let s = this.$store.state
    if (s.playlistType === 'album' && s.playlistId === id) this.current = true
    axios.get(`/api/album/${id}`).then(res => this.album = res.data)
  }
}
</script>

<style>
.album {
  padding: 0px 20px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.album-name {
  box-sizing: border-box;
  font-weight: bold;
  padding-top: 20px;
  text-align: center;
  width: 100%;
  font-size: 150%;
}

.album-artist {
  box-sizing: border-box;
  padding: 7px 0px 20px 0px;
  text-align: center;
  width: 100%;
  font-size: 90%;
  color: #aaaaaa;
  cursor: pointer;
}

.album-artist:hover {
  color: #777777;
}

.album-options {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
}
</style>