<template>
  <a-portal :value="value">
    <a-overlay
      :value="value"
      :strict="strict"
      @input="$emit('input', $event)"
      class="a-modal"
      :canClose="canClose"
    >
      <div>
        <slot></slot>
      </div>
    </a-overlay>
  </a-portal>
</template>

<script>
import APortal from '@/components/APortal'
import AOverlay from '@/components/AOverlay'

export default {
  components: {
    APortal,
    AOverlay
  },
  props: {
    value: { type: Boolean, default: false },
    strict: { type: Boolean, default: true },
    canClose: { type: Boolean, default: true }
  }
}
</script>

<style >
.a-modal {
  display: flex;
  justify-content: center;
  align-items: center;
}

.a-modal>div {
  max-height: 80%;
  max-width: 80%;
  border-radius: 7px;
  box-shadow: 0px 0px 6px 0px rgba(0,0,0,0.3);
  background-color: white;
  overflow: auto;
}
</style>
