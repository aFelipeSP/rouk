<template>
  <div class="player">
    <div class="player-button" @click="update"><icon-update /></div>
    <div class="player-button" @click="random"><icon-random /></div>
    <div class="player-button" @click="last"><icon-last /></div>
    <div class="player-play" @click="togglePlay">
      <icon-pause v-if="playing"/>
      <icon-play v-else/>
    </div>
    <div class="player-button" @click="next"><icon-next /></div>
    <div class="player-button" @click="repeat"><icon-repeat /></div>
    <div class="player-button" @click="addSong"><icon-plus /></div>
    <a-playlist-song-modal v-model="playlistSongModal" :song="(currentSong || {}).id"/>
  </div>
</template>


<script>
import IconUpdate from '@/icons/update.vue'
import IconRandom from '@/icons/random.vue'
import IconLast from '@/icons/last.vue'
import IconPause from '@/icons/pause.vue'
import IconPlay from '@/icons/play.vue'
import IconNext from '@/icons/next.vue'
import IconRepeat from '@/icons/repeat.vue'
import IconPlus from '@/icons/plus.vue'
import APlaylistSongModal from '@/components/AModal'

import axios from 'axios'

export default {
  components: {
    IconUpdate,
    IconRandom,
    IconLast,
    IconPause,
    IconPlay,
    IconNext,
    IconRepeat,
    IconPlus,
    APlaylistSongModal
  },
  data () {
    return {
      playlistSongModal: false
    }
  },
  methods: {
    update () {
      axios.post('/api/update')
    },
    random () {
      axios.post('/api/random')
    },
    last () {
      axios.post('/api/last')
    },
    togglePlay () {
      axios.post('/api/toggle-play')
    },
    next () {
      axios.post('/api/next')
    },
    repeat () {
      axios.post('/api/repeat')
    },
    addSong () {
      if (this.currentSong != null) {
        this.playlistSongModal = true
      }
    }
  },
  computed: {
    playing () { return this.$store.state.playing },
    currentSong () { return this.$store.state.currentSong }
  }
}
</script>

<style>
.player {
  --player-size: 20px;
  padding: 10px 0px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f1f1f1;
}

.player-button {
  border-radius: 9999999px;
  padding: 4vw;
  flex: 1;
  cursor: pointer;
}

.player-button:hover {
  background-color: #c5c5c5;
}

.player-play {
  padding: 4vw;
  background-color: #a0a8cc;
  box-shadow: 0px 0px 6px 1px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  border-radius: 9999999px;
  flex: 1.5;
}

.player-play:hover {
  background-color: #7e97af;
}

@media only screen and (min-width: 300px) {
  .player-button {
    padding: calc(var(--player-size)*0.6);
    flex: 0 1 auto;
    width: var(--player-size);
    height: var(--player-size);
  }

  .player-play {
    padding: calc(var(--player-size)*0.6);
    flex: 0 1 auto;
    width: calc(var(--player-size)*1.3);
    height: calc(var(--player-size)*1.3);
  }
}
</style>