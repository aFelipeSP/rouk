<template>
  <div id="app">
    <div style="flex: 1;overflow: auto">
      <router-view/>
    </div>
    <n-player />
    <div style="display:flex;align-items:center;background-color:#dddddd">
      <div v-for="(i, page) in pages" :key="i"
        v-text="page"
        class="nav-btn"
        @click="$router.push({name: page.toLowerCase()})"
        :style="$route.name === page.toLowerCase() ? 'font-weight:bold' : ''"
      />
    </div>
  </div>
</template>

<script>
import NPlayer from '@/components/play.vue'

export default {
  components: {
    NPlayer
  },
  data () {
    return {
      pages: ['Home', 'Library']
    }
  }
}
</script>

<style>
html, body {
  height: 100%;
  width: 100%;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #374f68;
  display: flex;
  flex-direction: column;
  height: 100%;
}

#nav-btn {
  font-size: 110%;
}

#r-title {
  font-size: 105%;
  font-weight: bold;
}

</style>
