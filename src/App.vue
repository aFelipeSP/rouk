<template>
  <div id="app">
    <div style="box-shadow: 0px -1px 10px 1px rgba(0,0,0,0.3)">
      <a-song-bar v-if="song != null" :progress="progress" :song="song"/>
      <a-player />
    </div>
    <div style="flex: 1;overflow: auto">
      <router-view/>
    </div>
    <!-- <div style="display:flex;align-items:center;background-color:#dddddd">
      <div v-for="(page, i) in pages" :key="i"
        v-text="page"
        class="nav-btn"
        @click="$router.push({name: page.toLowerCase()})"
        :style="$route.name === page.toLowerCase() ? 'font-weight:bold' : ''"
      />
    </div> -->
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
html, body {
  margin: 0px;
  height: 100%;
  width: 100%;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #495057;
  display: flex;
  flex-direction: column-reverse;
  height: 100%;
}

.beam {
  font-size: 80%;
  padding: 5px 10px;
  border-radius: 9999999px;
}


/* width */
::-webkit-scrollbar {
  width: 12px;
}
/* Track */
::-webkit-scrollbar-track {
  background-color: transparent;
}
/* Handle */
::-webkit-scrollbar-thumb {
  background-color: #bbbbbb;
  border-radius: 100000px;
  background-clip: padding-box;
  border: 3px solid rgba(0, 0, 0, 0);
}
/* Handle on hover */
::-webkit-scrollbar-thumb:hover {
  background-color: #bbbbbb;
}
</style>
