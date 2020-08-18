<template>
  <div class="song">
    <div
      class="song-property"
      v-for="(prop, i) in props"
      :key="i"
    >
      <b>{{prop}}</b> {{song[prop]}}
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      props: ['name', 'duration', 'year', 'artist', 'album'],
      song: null
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
  padding: 10px;
  padding: 10px;
}

.song-property {
  padding: 10px;
}
</style>
