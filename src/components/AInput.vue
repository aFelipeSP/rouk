<template>
  <a-dropdown class="a-input" v-model="opened">
    <template #clickable>
      <input :type="type" :value="value" :name="name" style="display:none">
      <div
        tabindex="0"
        contenteditable="true"
        :class="'a-input-box '+type"
        @keydown="onkeydown"
        @keyup="onkeyup"
        @paste="textPasted"
        spellCheck="false"
        autocapitalize="off"
        autocomplete="off"
        autocorrect="off"
        data-gramm="false"
        ref="text"
      />
      <icon-clear
        v-if="clearable"
        class="a-input-clear"
        @click="clear"
      />
    </template>
    <template #dropdown>
      <div
        v-for="(el, index) in suggestions_"
        :key="index"
        :class="[
          'a-input-suggestion',
          (suggestionsPos === index) ? 'selected' : ''
        ]"
        v-text="el"
        @click="suggestionClick(el)"
      />
    </template>
  </a-dropdown>
</template>

<script>
import ADropdown from '@/components/ADropdown'
import IconClear from '@/icons/clear'
/* eslint-disable no-console */

let numRegex = /^[-+]?(\.|\d+|\.\d+|\d+\.|\d+\.\d+)(e|e\d+|e[+-]|e[+-]\d+|)?$/i

export default {
  components: {
    ADropdown,
    IconClear
  },
  props: {
    type: {
      type: String,
      default: 'text',
      validator: function (value) {
        return ['number', 'text'].indexOf(value) !== -1
      }
    },
    name: String,
    debounce: { type: Number, default: 0 },
    value: [String, Number],
    multiline: Boolean,
    placeholder: String,
    icon: String,
    clearable: Boolean,
    suggestions: Array,
    min: Number,
    max: Number
  },
  data () {
    return {
      opened: false,
      suggestionsPos: null,
      suggestions_: null,
      timeout: null,
      initCount: 0,
      suggestionClicked: false
    }
  },
  watch: {
    value: {
      handler () {
        this.change_()
      },
      immediate: true
    },
    type () {
      this.$emit('input', null)
    }
  },
  methods: {
    suggestionClick (el) {
      this.suggestionClicked = true
      this.suggestionsPos = null
      this.$emit('input', el)
      this.$emit('selected', el)
    },
    change_ () {
      if (this.$refs.text != null) {
        this.initCount = 0
        this.change()
      } else if (this.initCount < 20) {
        this.initCount++
        setTimeout(this.change_, 100)
      }
    },
    onclick () {
      this.updateSuggestions(this.value)
    },
    updateSuggestions (value) {
      if (value == null || this.type !== 'text') {
        this.opened = false
        return
      }
      let suggestions = (this.suggestions || []).filter(el => 
        el.toLowerCase().includes(
          value.toLowerCase()) && el != value
      )
      if (suggestions.length > 0) this.opened = true
      else this.opened = false
      this.suggestions_ = suggestions
    },
    change () {
      let value = this.value
      let text = this.$refs.text.innerText
      if (this.type === 'number') {
        let text_ = Number(text)
        if (isNaN(text_) && numRegex.test(text) || value == text_) return
      } else {
        this.updateSuggestions(this.value)
        if (value === text) return
      }
      let pos = this.getCurrentCursorPosition()

      if (this.suggestionClicked) {
        this.suggestionClicked = false
        pos = value.length || 0
      }

      this.$refs.text.innerText = value || ''
      if (pos != null) {
        this.setCurrentCursorPosition(pos)
      }
    },
    onkeydown (e) {
      if (this.type === 'text') {
        if (this.opened) {
          if (e.key === 'ArrowDown') {
            if (this.suggestionsPos == null)
              this.suggestionsPos = 0
            else
              this.suggestionsPos = Math.min(this.suggestionsPos + 1, this.suggestions_.length - 1)
            e.preventDefault()
            e.stopPropagation()
            return
          } else if (e.key === 'ArrowUp') {
            if (this.suggestionsPos == null)
              this.suggestionsPos = this.suggestions_.length - 1
            else
              this.suggestionsPos = Math.max(this.suggestionsPos - 1, 0)
            e.preventDefault()
            e.stopPropagation()
            return
          } else if (e.key === 'Enter' && this.suggestionsPos != null) {
            this.suggestionClicked = true
            this.$emit('input', this.suggestions_[this.suggestionsPos])
            this.suggestionsPos = null
            e.preventDefault()
            e.stopPropagation()
            return
          }
        }
        if (e.key === 'Enter' && !this.multiline) {
          e.preventDefault()
          e.stopPropagation()
          return
        }
      } else if (this.type === 'number') {
        if (e.ctrlKey && ['c', 'v', 'a'].includes(e.key) ||
          ['ArrowLeft', 'ArrowRight'].includes(e.key)
        ) return
        let sel = window.getSelection()
        let r = numRegex
        let v = e.target.innerText
        let i = sel.focusOffset, j = sel.anchorOffset
        if (["Backspace", 'Delete'].includes(e.key)) {
          let str
          if (i !== j) {
            str = v.slice(0, Math.min(i,j)) + v.slice(Math.max(i,j))
          } else if (e.key === 'Backspace') {
            str = v.slice(0, i-1) + v.slice(i)
          } else if (e.key === 'Delete') {
            str = v.slice(0, i) + v.slice(i+1)
          }
          if (str === '' || r.test(str)) return
        } else if ('0123456789eE-+.'.includes(e.key)) {
          let str = v.slice(0, Math.min(i,j)) + e.key + v.slice(Math.max(i,j))
          if (r.test(str)) return
        }
        e.preventDefault()
        e.stopPropagation()
      }
    },
    onkeyup (e) {
      let value = e.target.innerText
      if (this.type === 'number') {
        if (value === '') value = null
        else {
          value = Number(value)
          value = isNaN(value) ? null : value
        }
      }
      this.emitInput(value)
    },
    getCurrentCursorPosition() {
      let sel = window.getSelection()
      if (sel.focusNode && this.$refs.text.contains(sel.focusNode)) {
        return sel.focusOffset
      }
    },
    setCurrentCursorPosition(count) {
      let node = this.$refs.text
      let selection = window.getSelection()
      let range = document.createRange()
      range.selectNode(node)
      range.setStart(node, 0)
      if (node.firstChild == null) {
        range.setEnd(node, 0)
      } else {
        range.setEnd(node.firstChild, count)
      }
      range.collapse(false)
      selection.removeAllRanges()
      selection.addRange(range)
    },
    textPasted (e) {
      // Stop data actually being pasted into div
      e.stopPropagation()
      e.preventDefault()

      let clipboardData = e.clipboardData || window.clipboardData
      let text = clipboardData.getData('Text')

      if ((this.type === 'text' && !this.multiline) || 'number' === this.type) {
        text = text.replace(/\r?\n|\r/gm, ' ')
      }

      if (this.type === 'number') {
        let sel = window.getSelection()
        let r = numRegex
        let v = e.target.innerText
        let i = sel.focusOffset, j = sel.anchorOffset
        if (i !== j) {
          if (!r.test(
            v.slice(0, Math.min(i,j)) + text + v.slice(Math.max(i,j))
          )) return
        } else {
          if (!r.test(v.slice(0, i)+ text+ v.slice(i))) return
        }
      }
      document.execCommand("insertHTML", false, text)
    },
    emitInput (value) {
      if (this.debounce === 0) {
        this.$emit('input', value)
      } else {
        clearTimeout(this.timeout)
        this.timeout = setTimeout(
          () => this.$emit('input', value), this.debounce)
      }
    },
    clear () {
      this.$emit('input', null)
      this.focus()
    },
    focus () {
      let text = this.$refs.text
      this.setCurrentCursorPosition(((text.firstChild || {}).length) || 0)
    }
  }
}
</script>

<style>
.a-input {
  width: 100%;
}
.a-input>.a-dropdown-clickable {
  width: 100%;
  margin: 0px;
  height: 100%;
  align-items: center;
  display: flex;
}
.a-input-clear {
  cursor: pointer;
  padding-left: 7px;
}
.a-input-box {
  width: 100%;
  white-space: pre-line;
  min-height: 1em;
  min-width: 2em;
  flex: 1;
  overflow: hidden;
}
.a-input-box:focus {
  background: none;
  outline: none;
}
.a-input-suggestion {
  padding: 10px;
  background-color: white;
  cursor: pointer;
}
.a-input-suggestion.selected {
  background-color: rgba(0,0,0,0.16);
}
</style>