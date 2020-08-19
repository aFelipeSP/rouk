<template>
  <div class="options">
    <div class="options-title">Options</div>
    <!-- <div class="options-item">
      <div class="options-key">Music Folder</div>
      <a-input class="options-input" :value="musicFolder" :debounce/>
    </div> -->
  </div>
</template>

<script>
// import AInput from '@/components/AInput'
// import axios from 'axios'

export default {
  components: {
    // AInput
  },
  data () {
    return {
      musicFolder: null
    }
  },
  methods: {
    // getMusicFolder () {
    //   axios.get('/api/options/music-folder').then(res => this.musicFolder = res.data)
    // },
    // setMusicFolder () {
    //   axios.post('/api/options/music-folder', {value: this.musicFolder}).then(() => {})
    // }
  }
}
</script>

<style>
.options {
  padding: 20px;
}

.options-title {
  font-size: 110%;
  font-weight: bold;
  padding: 10px 0px;
}

.options-item {
  padding: 10px 0px;
}

.options-key {
  font-size: 90%;
  font-weight: bold;
}

.options-input {
  padding: 10px 0px 0px 0px;
  border-bottom: 1px solid #dddddd;
}

</style>