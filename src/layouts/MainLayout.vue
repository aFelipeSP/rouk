<template>
  <div class="main-layout">
    <div style="box-shadow: 0px -4px 10px -1px rgba(0,0,0,0.2)">
      <a-song-bar v-if="song != null"/>
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
    song () { return this.$store.state.song }
  }
}
</script>

<style>
.main-layout {
  display: flex;
  flex-direction: column-reverse;
  height: 100%;
}

@media only screen and (min-width: 600px) {
  .main-layout {
    box-sizing: content-box;
    margin: 0 auto;
    box-shadow: 0px 0px 10000px 100px rgba(0,0,0,0.2);
    width: 600px
  }
}
</style>
