<template>
  <div class="player">
    <div class="player-button" @click="update"><icon-update /></div>
    <div class="player-button" @click="random"><icon-random /></div>
    <div class="player-button" @click="last"><icon-last /></div>
    <div class="player-play" @click="togglePlay"> <icon-play /></div>
    <div class="player-button" @click="next"><icon-next /></div>
    <div class="player-button" @click="repeat"><icon-repeat /></div>
    <div class="player-button"></div>
  </div>
</template>


<script>
import IconUpdate from '@/icons/update.vue'
import IconRandom from '@/icons/random.vue'
import IconLast from '@/icons/last.vue'
import IconPlay from '@/icons/play.vue'
import IconNext from '@/icons/next.vue'
import IconRepeat from '@/icons/repeat.vue'

import axios from 'axios'

export default {
  components: {
    IconUpdate,
    IconRandom,
    IconLast,
    IconPlay,
    IconNext,
    IconRepeat
  },
  methods: {
    update () {
      axios.post('/update')
    },
    random () {
      axios.post('/random')
    },
    last () {
      axios.post('/last')
    },
    togglePlay () {
      axios.post('/toggle-play')
    },
    next () {
      axios.post('/next')
    },
    repeat () {
      axios.post('/repeat')
    }
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