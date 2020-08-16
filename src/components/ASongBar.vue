<template>
  <div class="songbar">
    <div class="songbar-back" :style="progress_text" />
    <div ref="text" class="songbar-text">{{song}}</div>
  </div>
</template>


<script>
// import axios from 'axios'

export default {
  data () {
    return {
      scrollStart: null,
      progress: null,
    }
  },
  methods: {
    scroll (timestamp) {
      if (this.start == null) this.scrollStart = timestamp

      const elapsed = timestamp - this.scrollStart
      const el = this.$refs.text
      const range = el.scrollWidth - el.clientWidth

      el.scroll(elapsed*0.05, 0)
      if (el.scrollLeft < range) {
        window.requestAnimationFrame(this.scroll)
      } else {
        setTimeout(() => this.startScroll(), 3500)
      }

    },
    startScroll () {
      this.scrollStart = null
      this.$refs.text.scroll(0, 0)
      window.requestAnimationFrame(this.scroll)
    },
    play (timestamp) {
      if (this.start == null) this.start = timestamp
      const elapsed = timestamp - this.start
      this.progress = elapsed / this.duration
      if (elapsed < this.duration) {
        window.requestAnimationFrame(this.scroll)
      } else {
        setTimeout(() => this.startScroll(), 3500)
      }

    },
    startSong () {
      this.start = null
      this.$refs.text.scroll(0, 0)
      window.requestAnimationFrame(this.scroll)
    }
  },
  computed: {
    progress_text () {
      let text = 'background: linear-gradient(90deg, #bce6be '
      return text + `${this.progress}%, #ffffff00 ${this.progress}%)`
    },
    song () { return this.$store.state.currentSong },
    playing () { return this.$store.state.playing },
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

.songbar-back {
  z-index: -1;
  position: absolute;
  width: 100%;
  height: 100%;
  left: 0;
  top: 0;
}

</style>