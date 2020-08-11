import Vue from 'vue'
import uuidv4 from 'uuid/v4'
import router from '@/router'
import store from '@/store'
export default {
  props: {
    value: Boolean
  },
  data () {
    return {
      id: uuidv4(),
      vue: null,
    }
  },
  methods: {
    setup () {
      let el = document.createElement('div')
      el.dataset.aPortalId = this.id
      document.body.appendChild(el)
      let self = this
      this.vue = new Vue({
        router,
        store,
        el: `[data-a-portal-id="${self.id}"`,
        data () {
          return {
            content: null
          }
        },
        render (h) {
          if (Array.isArray(this.content)) {
            if (this.content.length === 1) return this.content[0]
            return h('div', this.content)
          }
          return this.content
        }
      })
    }
  },
  render () {
    if (this.value) {
      if (this.vue == null)
        this.setup()
      this.vue.content = this.$slots.default
    } else {
      if (this.vue != null) {
        this.vue.$el.parentNode.removeChild(this.vue.$el)
        this.vue.$destroy()
        this.vue = null
      }
    }
  },
  destroyed () {
    if (this.vue != null) {
      this.vue.$el.parentNode.removeChild(this.vue.$el)
      this.vue.$destroy()
      this.vue = null
    }
  }
}