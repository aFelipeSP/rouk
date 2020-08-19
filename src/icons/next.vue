<template>
  <svg style="display:block" viewBox="-.15 -.15 1.3 1.3"
    preserveAspectRatio="none" @click="$emit('click', $emit)"
  >
    <path d="M0 0L0.9 0.5L0 1z" fill="currentColor"/>
    <line x1=.9 y1=0 x2=.9 y2=1 stroke="currentColor" stroke-width="0.2" />
  </svg>
</template>

<script>
export default {}
</script>