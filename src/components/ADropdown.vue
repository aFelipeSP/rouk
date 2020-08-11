<template>
<div>
  <div
    ref="adropdown"
    class="a-dropdown-clickable"
  >
    <slot name="clickable"></slot>
  </div>
  <a-portal :value="value">
    <a-overlay
      :value="value"
      @input="$emit('input', $event)"
      :opacity="0"
    >
      <div
        class=a-dropdown-box
        :style="boxPosition"
      >
        <slot name="dropdown"></slot>
      </div>
    </a-overlay>
  </a-portal>
</div>
</template>

<script>
/* eslint-disable no-console */

export default {
  props: {
    value: Boolean,
    sameWidth: Boolean
  },
  data () {
    return {
      boxPosition: {}
    }
  },
  watch: {
    value (nvalue) {
      if (nvalue) {
        window.addEventListener('resize', this.onresize)
      } else {
        window.removeEventListener('resize', this.onresize)
      }
      this.onresize()
    }
  },
  methods: {
    onresize () {
      try {
        if (this.value) {
          let docEl = document.documentElement
          let rect = this.$refs.adropdown.getBoundingClientRect()
          let h = this.$refs.adropdown.clientHeight
          let rel_pos_y = (rect.y + h*0.5) / docEl.clientHeight
          let rel_pos_x = rect.x / docEl.clientWidth
          let boxPosition = {}
          if (this.sameWidth) boxPosition.width = rect.width + 'px'
          if (rel_pos_y > 0.5) {
            boxPosition.maxHeight = rect.y + 'px'
            boxPosition.bottom = 'calc(100vh - ' + rect.y + 'px)'
          } else {
            boxPosition.maxHeight = 'calc(100vh - ' + (rect.y + h) + 'px)'
            boxPosition.top = (rect.y + h) + 'px'
          }
          if (rel_pos_x > 0.5) {
            boxPosition.right = 'calc(100vw - ' + rect.right + 'px)'
          } else {
            boxPosition.left = rect.x + 'px'
          }
          this.boxPosition = boxPosition
        }
      } catch {
        // nothing
      }
    }
  },
  destroyed () {
    window.removeEventListener('resize', this.onresize)
  }
}
</script>

<style lang="sass">
.a-dropdown-box
  border-radius: 3px
  box-shadow: shadow(2.5px)
  position: absolute
  background-color: white
  overflow: auto
</style>
