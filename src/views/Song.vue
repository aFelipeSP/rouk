<template>
  <div class="song">
    <div class="song-name">{{song.name}}</div>
    <div class="song-options">
      <div @click="play" class="btn-rnd --c-b-green">Play</div>
    </div>
    <div class="song-property"><b>Artist:</b>&nbsp;
      <span class="song-link" @click="goTo('artist')"  v-text="artist" />
    </div>
    <div class="song-property"><b>Album:</b>&nbsp;
      <span class="song-link" @click="goTo('album')" v-text="album" />
    </div>
    <div class="song-property"><b>Year:</b> {{song.year}}</div>
    <div class="song-property"><b>Duration:</b> {{duration}}</div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      props: ['duration', 'year', 'artist', 'album'],
      song: {}
    }
  },
  methods: {
    play () {
      axios.post(`/api/play/song/${this.song.id}`).then(
        () => console.log('playing song')
      )
    },
    goTo (prop) {
      this.$router.push(
        { name: prop, params: {id: this.song[prop].id}}
      ).catch(()=>{})
    }
  },
  computed: {
    artist () { return (this.song.artist || {}).name },
    album () { return (this.song.album || {}).name },
    duration () {
      let d = this.song.duration
      let mins_ = d / 60
      let mins = Math.trunc(mins_)
      let secs = Math.round((mins_ - mins) * 60).toString().padStart(2, '0')
      return `${mins}:${secs}`
    }
  },
  mounted () {
    let id = this.$route.params.id
    axios.get('/api/song/'+id).then(res => this.song = res.data)
  }
}
</script>

<style>
.song {
  padding: 0px 20px;
}

.song-name {
  box-sizing: border-box;
  font-weight: bold;
  padding: 20px;
  text-align: center;
  width: 100%;
  font-size: 150%;
}

.song-options {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
}

.song-property {
  padding: 10px;
}

.song-link {
  cursor: pointer
}

.song-link:hover {
  color: #bbbbbb;
}
</style>
