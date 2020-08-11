<template>
  <div class="library">
    <div class="library-search-options">
      <div
        v-for="(i, label) in labels"
        :key="'l' + i"
        class="library-search-option"
        @click="setLabel(label)"
        v-text="label"
      >
    </div>
    <div class="library-search">
      <icon-search />
      <a-input class="library-search-input" v-model="searchValue" />
    </div>
    <div class="library-items">
      <div
        v-for="(j, item) in data"
        :key="'l' + j"
        class="library-item"
        @click="setLabel(item)"
        v-text="item"
      >
    </div>
  </div>
</template>

<script>
import AInput from '@/components/AInput'
import IconSearch from '@/icons/search'

export default {
  components: {
    AInput,
    IconSearch
  },
  data () {
    return {
      searchValue: null,
      data: []
    }
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
