<template>
  <div class="album">
    <div class="album-name" v-text="album.name" />
    <div style="font-size:120%;font-weight:bold">Songs</div>
    <a-list label="song" :data="album.songs" />
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
      album: null
    }
  },
  mounted () {
    let id = this.$route.params.id
    axios.get('/api/album/'+id).then(res => this.album = res.data)
  }
}
</script>
