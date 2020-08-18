<template>
  <div class="a-search-bar" ref="searchBox" @click="focusInput">
    <icon-search style="width:25px;margin:15px;"/>
    <a-input
      ref="searchInput"
      class="a-search-bar-input"
      :value="value"
      @input="$emit('input', $event)"
      :debounce="1000"
    />
    <icon-clear @click="clearSearch"
      style="width:20px;padding:10px;cursor:pointer"
    />
  </div>
</template>

<script>
import AInput from '@/components/AInput'
import IconSearch from '@/icons/search'
import IconClear from '@/icons/clear'

export default {
  components: {
    AInput,
    IconSearch,
    IconClear
  },
  props: {
    value: String
  },
  methods: {
    clearSearch () {
      this.searchValue = null
      this.$refs.searchInput.focus()
    },
    focusInput (ev) {
      if (ev.target == this.$refs.searchBox) {
        this.$refs.searchInput.focus()
      }
    }
  }
}
</script>

<style>
.a-search-bar {
  display: flex;
  align-items: center;
  background-color: #eeeeee;
  cursor: text;
}

.a-search-bar-input {
  font-size: 110%;
}

</style>
