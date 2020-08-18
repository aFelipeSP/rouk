<template>
  <div class="artist">
    <div class="artist-name" v-text="artist.name" />
    <div style="font-size:120%;font-weight:bold">Albums</div>
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
      artist: null
    }
  },
  mounted () {
    let id = this.$route.params.id
    axios.get('/api/artist/'+id).then(res => this.artist = res.data)
  }
}
</script>
