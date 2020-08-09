<template>
  <div class="home">
    <div class="r-title">Más escuchados</div>
    <div class="home-list">
      <div clas="home-list-item" v-for="(i, playlist) in freqPlaylists" :key="i">
        <img src="" alt="">
        <div>{{playlist}}</div>
      </div>
    </div>
  </div>
</template>

<style>
.home {
  display: flex;
  flex-direction: column;
}

.home-list {
  overflow: auto;
  flex: 1;
}

.home-list-item {
  display: flex;
  align-items: center;
}

.home-list-item.img {
  height: 100px;
  width: 100px;
}

/* .home-list-item.title {
} */
</style>

<script>

export default {
  name: 'Home',
  components: {
  }
}
</script>
