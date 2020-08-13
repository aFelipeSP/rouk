<template>
  <div class="library">
    <div class="library-search-options">
      <div
        v-for="(i, label) in labels"
        :key="'l' + i"
        class="library-search-option"
        @click="setLabel(label)"
        v-text="label"
      />
    </div>
    <div class="library-search">
      <icon-search />
      <a-input
        class="library-search-input"
        v-model="searchValue"
        :debounce="1000"
      />
    </div>
    <div class="library-items">
      <div
        v-for="(j, item) in data"
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
      labels: ['song', 'playlist', 'artist'],
      searchValue: null,
      data: [],
      label: null
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
  display: grid;
  grid-template-columns: 50px 50px 50px 50px;
  grid-template-rows: auto;
  grid-template-areas: 
    "header header header header"
    "main main . sidebar"
    "footer footer footer footer";
}

@media only screen and (min-width: 1000px) {
  
}
</style>
