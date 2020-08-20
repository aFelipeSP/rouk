<template>
  <div class="songbar">
    <div class="songbar-back" :style="progress_text" />
    <div ref="text" class="songbar-text">
      <span class="songbar-text-item">
        <b>{{song.track}}.&nbsp;{{song.name}}</b>,
      </span>
      <span class="songbar-text-item">
        <b>Artist:&nbsp;</b>{{song.artist.name}},
      </span>
      <span class="songbar-text-item">
        <b>Album:&nbsp;</b>{{song.album.name}}
      </span>
      <span class="songbar-text-item"><b>Year:&nbsp;</b>{{song.year}}</span>
    </div>
  </div>
</template>


<script>
// import axios from 'axios'

export default {
  data () {
    return {
      scrollStart: null,
    }
  },
  methods: {
    scroll (timestamp) {
      if (this.scrollStart == null) this.scrollStart = timestamp

      const elapsed = timestamp - this.scrollStart
      const el = this.$refs.text
      const range = el.scrollWidth - el.clientWidth

      el.scroll(elapsed*0.025, 0)
      if (el.scrollLeft < range) {
        window.requestAnimationFrame(this.scroll)
      } else {
        setTimeout(() => {
          el.scroll(0, 0)
          setTimeout(() => this.startScroll(), 1500)
        }, 1500)
      }

    },
    startScroll () {
      this.scrollStart = null
      this.$refs.text.scroll(0, 0)
      window.requestAnimationFrame(this.scroll)
    }
  },
  computed: {
    progress_text () {
      let progress = 100*this.$store.state.time / this.song.duration
      let text = 'background: linear-gradient(90deg, #bce6be '
      return text + `${progress}%, #ffffff00 ${progress}%)`
    },
    song () { return this.$store.state.song },
    duration () { return this.song.duration*1000 }
  },
  mounted () {
    while (this.$refs.text == null) {
      //
    }
    this.startScroll()
  }
}
</script>

<style>
.songbar {
  position: relative;
  height: 1.5em;
  overflow: hidden;
}

.songbar-text {
  padding: 2px;
  overflow: hidden;
  white-space: nowrap;
}

.songbar-text-item {
  margin-right: 20px;
}

.songbar-text-item:last-child {
  margin-right: 0px;
}

.songbar-back {
  z-index: -1;
  position: absolute;
  width: 100%;
  height: 100%;
  left: 0;
  top: 0;
}

</style>