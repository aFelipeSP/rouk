<template>
  <div class="a-items">
    <div
      v-for="(item, j) in data"
      :key="'l' + j"
      class="a-item"
      :style="
        isCurrent && currentTrack === item.id
        ? 'background-color: #9de59d' : ''
      "
    >
      <div style="flex:1" @click="goTo(item.id)">
        <div class="a-item-name" v-text="item.name" />
        <div v-if="['song', 'album'].includes(label)"
          class="a-item-artist" v-text="item.artist"
        />
        <div v-if="'song' === label"
          class="a-item-album" v-text="item.album"
        />
      </div>
      <div v-if="'song' === label" class="a-item-btn"
        @click="addSong(item.id)" style="margin-right:5px"
      >
        <icon-plus />
      </div>
      <div class="a-item-btn" @click="play(item.id)"><icon-play /></div>
    </div>
    <a-playlist-song-modal v-model="playlistSongModal" :song="playlistSong"/>
  </div>
</template>

<script>
import IconPlus from '@/icons/plus'
import IconPlay from '@/icons/play'
import APlaylistSongModal from '@/components/APlaylistSongModal'

import axios from 'axios'

export default {
  components: {
    IconPlus,
    IconPlay,
    APlaylistSongModal
  },
  props: {
    data: {type: Array, default: () => []},
    label: {
      type: String,
      validator: (v) => ['playlist', 'artist', 'song', 'album'].includes(v)
    },
    current: { type: Boolean, default: false }
  },
  data () {
    return {
      playlistSong: null,
      playlistSongModal: false
    }
  },
  methods: {
    play (id_) {
      axios.post(`/api/play/${this.label}/${id_}`)
    },
    // eslint-disable-next-line no-unused-vars
    addSong (id_) {
      this.playlistSong = id_
      this.playlistSongModal = true
    },
    // eslint-disable-next-line no-unused-vars
    goTo (id_) {
      this.$router.push({ name: this.label, params: {id: id_}}).catch(()=>{})
    }
  },
  computed: {
    currentTrack () {
      return (this.$store.state.song || {}).id
    },
    isCurrent () {
      return this.label === 'song' && this.current
    }
  }
}
</script>

<style>
.a-items {
  flex: 1;
  overflow: auto;
}

.a-item {
  padding: 10px;
  border-bottom: 1px solid #eeeeee;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.a-item:hover {
  background-color: #f0f0f0;
}

.a-item-name {
  padding: 2px 0px;
}

.a-item-artist {
  padding: 2px 0px;
  font-size: 80%;
  color: #0a9205;
}

.a-item-album {
  padding: 2px 0px;
  font-size: 80%;
  color: #6b0c0c;
}

.a-item-btn {
  padding: 8px;
  border-radius: 9999px;
  width: 15px;
  box-shadow: 0px 0px 10px 1px rgba(0,0,0,0.2)
}

.a-item-btn:hover {
  background-color: #dddddd;
}

.a-item:last-child {
  border-bottom: none;
}
</style>
