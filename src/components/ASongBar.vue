<template>
  <div class="songbar">
    <div style="margin: 0px 6px;font-size:80%">{{elapsedText}}</div>
    <div ref="songbar" class="songbar-bar" @click="selectPosition">
      <div ref="bar" class="songbar-back" />
      <div ref="text" class="songbar-text">
        <span class="songbar-text-item">
          <b>{{song.track ? (song.track + '.') : ''}}&nbsp;{{song.name}}</b>
        </span>
        <span class="songbar-text-item">
          <b>Artist:&nbsp;</b>{{song.artist.name}}
        </span>
        <span class="songbar-text-item">
          <b>Album:&nbsp;</b>{{song.album.name}}
        </span>
        <span class="songbar-text-item"><b>Year:&nbsp;</b>{{song.year}}</span>
      </div>
    </div>
    <div @click="goToCurrent" class="songbar-info">
      <div>i</div>
    </div>
  </div>
</template>


<script>
import axios from 'axios'
import { minsAndSecs } from '@/utils.js'

export default {
  data () {
    return {
      scrollStart: null,
      playStart: null,
      elapsed: 0
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
    },
    playFrame (timestamp) {
      if (!this.playing) return
      if (this.playStart == null) this.playStart = timestamp

      this.elapsed = this.time + timestamp - this.playStart
      const el = this.$refs.bar

      el.style.width = (100 * this.elapsed / this.duration) + '%'

      if (this.elapsed < this.duration) {
        window.requestAnimationFrame(this.playFrame)
      } else {
        el.style.width = '0%'
      }
    },
    startPlay () {
      this.playStart = null
      this.$refs.bar.style.width = (100 * this.time / this.duration) + '%'
      
      if (this.playing) {
        this.elapsed = 0
        window.requestAnimationFrame(this.playFrame)
      }
    },
    goToCurrent () {
      this.$router.push({
        name: this.$store.state.playlistType,
        params: {id: this.$store.state.playlistId}
      }).catch(() => {})
    },
    selectPosition (e) {
      let el = this.$refs.songbar
      let b = el.getBoundingClientRect()
      let x = e.clientX - b.x
      let position = Math.round(this.song.duration * x / el.offsetWidth)
      axios.post(`/api/position/${position}`)
    }
  },
  watch: {
    update () { this.startPlay() }
  },
  computed: {
    song () { return this.$store.state.song },
    duration () { return this.song.duration*1000 },
    playing () { return this.$store.state.playing },
    time () { return this.$store.state.time*1000 },
    update () { return this.$store.state.update },
    elapsedText () { return minsAndSecs(this.elapsed/1000) }
  },
  mounted () {
    while (this.$refs.text == null) {
      //
    }
    this.startScroll()
    this.startPlay()
  }
}
</script>

<style>
.songbar {
  display: flex;
  align-items: center;
  background-color: #f1f1f1;
}

.songbar-info {
  margin: 0px 7px;
  display: flex;
  border: 2px solid currentcolor;
  width: 1.5em;
  height: 1.5em;
  align-items: center;
  justify-content: center;
  font-size: 90%;
  font-family: monospace;
  border-radius: 99999px;
  font-weight: bold;
  cursor: pointer;
}


.songbar-bar {
  flex: 1;
  position: relative;
  height: 1.5em;
  overflow: hidden;
  background-color: white;
}

.songbar-text {
  position: absolute;
  overflow: hidden;
  white-space: nowrap;
  width: 100%;
  left: 0px;
  top: 50%;
  transform: translateY(-50%);
}

.songbar-text-item {
  margin: 0px 10px;
}

.songbar-back {
  background-color: #9de59d;
  height: 100%;
}


</style>