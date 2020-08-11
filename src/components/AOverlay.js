
export default {
  props: {
    value: { type: Boolean, default: false },
    strict: { type: Boolean, default: true },
    opacity: { type: Number, default: 0.4 },
    canClose: { type: Boolean, default: true }
  },
  render (h) {
    let style = {
        position: 'fixed',
        zIndex: '5000',
        left: '0',
        top: '0',
        width: '100%',
        height: '100%',
        backgroundColor: `rgba(0,0,0,${this.opacity})`
    }
    if (!this.strict && !this.value) style.display = 'none'
    else if (!this.strict || (this.strict && this.value)) {
      return h(
        'div', {
          ref: 'overlay',
          on: { click: (ev) => {
            if (this.canClose && ev.target == this.$refs.overlay) {
              this.$emit('input', false)
            }
          }},
          style
        },
        this.$slots.default
      )
    }
  }
}
