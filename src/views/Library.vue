<template>
  <div class="library">
    <div style="box-shadow: 0px 0px 10px 1px rgba(0,0,0,0.3)">
      <div class="library-search-options">
        <div
          v-for="(label_, i) in labels"
          :key="'l' + i"
          class="library-search-option"
          @click="setLabel(label_)"
          :style="(label_ === label) ? 'font-weight:bold' : ''"
          v-text="label_"
        />
      </div>
      <div class="library-search" ref="searchBox" @click="focusInput">
        <icon-search style="width:25px;margin:15px;"/>
        <a-input
          ref="searchInput"
          class="library-search-input"
          v-model="searchValue"
          :debounce="1000"
        />
        <icon-clear @click="clearSearch"
          style="width:20px;padding:10px;cursor:pointer"
        />
      </div>
    </div>
    <div class="library-items">
      <div
        v-for="(item, j) in data"
        :key="'l' + j"
        class="library-item"
      >
        <div style="flex:1" @click="goTo(item)">
          <div class="library-item-name" v-text="item.name" />
          <div v-if="['song', 'album'].includes(label)"
            class="library-item-artist" v-text="item.artist"
          />
          <div v-if="'song' === label"
            class="library-item-album" v-text="item.album"
          />
        </div>
        <div v-if="'song' === label" class="library-item-btn"
          @click="addSong" style="margin-right:5px"
        ><icon-plus /></div>
        <div class="library-item-btn" @click="playSong"><icon-play /></div>
      </div>
    </div>
  </div>
</template>

<script>
import AInput from '@/components/AInput'
import IconSearch from '@/icons/search'
import IconClear from '@/icons/clear'
import IconPlus from '@/icons/plus'
import IconPlay from '@/icons/play'
import axios from 'axios'

export default {
  components: {
    AInput,
    IconSearch,
    IconClear,
    IconPlus,
    IconPlay
  },
  data () {
    return {
      labels: ['playlist', 'artist', 'song', 'album'],
      searchValue: null,
      data: [],
      label: 'playlist'
    }
  },
  methods: {
    playSong () {
    },
    // eslint-disable-next-line no-unused-vars
    addSong (song) {
    },
    // eslint-disable-next-line no-unused-vars
    goTo (item) {
    },
    clearSearch () {
      this.searchValue = null
      this.$refs.searchInput.focus()
    },
    setLabel(label) {
      this.searchValue = null
      this.label = label
      this.search()
    },
    search () {
      axios.get(`/api/${this.label}?q=${this.searchValue || ''}`).then(
        a => {this.data = a.data}
      )
    },
    focusInput (ev) {
      if (ev.target == this.$refs.searchBox) {
        this.$refs.searchInput.focus()
      }
    }
  },
  watch: {
    searchValue: {
      handler () {
        this.search()
      },
      immediate: true
    }
  },
  mounted () {
    this.search()
  }
}
</script>

<style>
.library {
  height: 100%;
  overflow: auto;
  display: flex;
  flex-direction: column;
}

.library-search-options {
  font-size: 90%;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #dddddd;
  text-align: center;
}

.library-search-option {
  flex: 1;
  padding: 10px;
  border-left: 1px solid #dddddd;
  cursor: pointer;
}

.library-search-option:hover {
  background-color: #dddddd;
}

.library-search {
  display: flex;
  align-items: center;
  background-color: #eeeeee;
  cursor: text;
}

.library-search-input {
  font-size: 110%;
}

.library-items {
  flex: 1;
  overflow: auto;
}

.library-item {
  padding: 10px;
  border-bottom: 1px solid #eeeeee;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.library-item-name {
  padding: 2px 0px;
}

.library-item-artist {
  padding: 2px 0px;
  font-size: 80%;
  color: #0a9205;
}

.library-item-album {
  padding: 2px 0px;
  font-size: 80%;
  color: #6b0c0c;
}

.library-item-btn {
  padding: 8px;
  border-radius: 9999px;
  width: 15px;
  box-shadow: 0px 0px 10px 1px rgba(0,0,0,0.2)
}

.library-item-play:hover {
  background-color: #dddddd;
}

.library-item:last-child {
  border-bottom: none;
}

@media only screen and (min-width: 1000px) {
  
}
</style>
