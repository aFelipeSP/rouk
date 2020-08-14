<template>
  <div class="library">
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
    <div class="library-search">
      <icon-search style="width:20px;margin:0px 10px;"/>
      <a-input
        class="library-search-input"
        v-model="searchValue"
        :debounce="1000"
      />
    </div>
    <div class="library-items">
      <div
        v-for="(item, j) in data"
        :key="'l' + j"
        class="library-item"
        @click="setLabel(item)"
        v-text="item"
      />
    </div>
  </div>
</template>

<script>
import AInput from '@/components/AInput'
import IconSearch from '@/icons/search'
import axios from 'axios'

export default {
  components: {
    AInput,
    IconSearch
  },
  data () {
    return {
      labels: ['song', 'playlist', 'artist', 'album'],
      searchValue: null,
      data: [],
      label: 'playlist'
    }
  },
  methods: {
    setLabel(label) {
      this.searchValue = null
      this.label = label
      if (label === 'song') {
        axios.get('/song').then(a => {this.data = a.data})
      } else if (label === 'playlist') {
        axios.get('/playlist').then(a => {this.data = a.data})
      }else if (label === 'artist') {
        axios.get('/artist').then(a => {this.data = a.data})
      }
    },
    search () {
      axios.get(`/search/${this.label}?q=${this.searchValue || ''}`).then(
        a => {this.data = a.data}
      )
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
  padding: 20px;
  box-shadow: 0px 5px 5px 0px rgba(59, 45, 45, 0.2);
}

.library-search-input {
  border-bottom: 1px solid #cccccc
}

.library-items {
  flex: 1;
  overflow: auto;
  padding: 20px;
}

@media only screen and (min-width: 1000px) {
  
}
</style>
