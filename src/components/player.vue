<template>
  <div class="player">
    <div
      class="player-button"
      @click="last()"
    >
      <icon-last />
    </div>
    <div
      class="player-play"
      @click="togglePlay()"
    >
      <icon-play />
    </div>
    <div
      class="player-button"
      @click="next()"
    >
      <icon-next />
    </div>
  </div>
</template>


<script>
import IconLast from '@/icons/last.vue'
import IconPlay from '@/icons/play.vue'
import IconNext from '@/icons/next.vue'
export default {
  components: {
    IconLast,
    IconPlay,
    IconNext
  },
  methods: {
    last () {

    },
    togglePlay () {

    },
    next () {
      
    }
  }
}
</script>

<style>
.player {
  display: flex;
  align-items: center;
}

.player-button {
  flex: 1;
  cursor: pointer;
}

.player-button:hover {
  background-color: #c5c5c5;
}

.player-play {
  border-radius: 9999999px;
  width: 50px;
  height: 50px;
}
</style>