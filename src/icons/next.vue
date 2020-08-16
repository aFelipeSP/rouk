<template>
  <svg style="display:block" viewBox="0 0 1 1"
    preserveAspectRatio="none" @click="$emit('click', $emit)"
  >
    <path d="M0 0L1 0.5L0 1z" fill="currentColor"/>
    <line x1=1 y1=0 x2=1 y2=1 stroke="currentColor" stroke-width="0.4" />
  </svg>
</template>

<script>
export default {}
</script>