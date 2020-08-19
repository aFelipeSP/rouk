<template>
  <div class="artist">
    <div class="artist-name" v-text="artist.name" />
    <div class="artist-options">
      <div @click="play" class="btn-rnd --c-b-green">Play</div>
    </div>
    <div style="font-size:120%;font-weight:bold;margin:20px 0px;">Albums</div>
    <a-list label="album" :data="artist.albums" />
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
      artist: {}
    }
  },
  methods: {
    play () {
      axios.post(`/api/play/artist/${this.artist.id}`).then(
        () => console.log('playing artist')
      )
    }
  },
  mounted () {
    let id = this.$route.params.id
    axios.get(`/api/artist/${id}`).then(res => this.artist = res.data)
  }
}
</script>

<style>
.artist {
  padding: 0px 20px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.artist-name {
  box-sizing: border-box;
  font-weight: bold;
  padding: 20px;
  text-align: center;
  width: 100%;
  font-size: 150%;
}

.artist-artist {
  box-sizing: border-box;
  padding: 7px 0px 20px 0px;
  text-align: center;
  width: 100%;
  font-size: 90%;
  color: #aaaaaa;
  cursor: pointer;
}

.artist-artist:hover {
  color: #777777;
}

.artist-options {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
}
</style>