<template>
  <div class="main-layout">
    <div style="box-shadow: 0px -1px 10px 1px rgba(0,0,0,0.3)">
      <a-song-bar v-if="song != null" :progress="progress" :song="song"/>
      <a-player />
    </div>
    <div style="flex: 1;overflow: auto">
      <router-view/>
    </div>
  </div>
</template>

<script>
import APlayer from '@/components/APlayer.vue'
import ASongBar from '@/components/ASongBar.vue'

export default {
  components: {
    APlayer,
    ASongBar
  },
  data () {
    return {
      pages: ['Home', 'Library']
    }
  },
  computed: {
    song () {
      return this.$store.state.currentSong
    },
    progress () {
      return this.$store.state.songProgress
    }
  }
}
</script>

<style>
.main-layout {
  display: flex;
  flex-direction: column-reverse;
  height: 100%;
}
</style>
