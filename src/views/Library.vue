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
      <a-search-bar v-model="searchValue"/>
    </div>
    <a-list :label="label" :data="data" />
  </div>
</template>

<script>
import AList from '@/components/AList'
import ASearchBar from '@/components/ASearchBar'
import axios from 'axios'

export default {
  components: {
    AList,
    ASearchBar
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
    setLabel(label) {
      this.searchValue = null
      this.label = label
      this.search()
    },
    search () {
      axios.get(`/api/${this.label}?q=${this.searchValue || ''}`).then(
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

</style>
