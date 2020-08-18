<template>
  <svg style="display:block" viewBox="0 0 1 1"
    preserveAspectRatio="none" @click="$emit('click', $emit)"
    stroke="currentColor" stroke-width="0.2"
  >
    <line x1="0" y1="0.1" x2="1" y2="0.1" />
    <line x1="0" y1="0.5" x2="1" y2="0.5" />
    <line x1="0" y1="0.9" x2="1" y2="0.9" />    
  </svg>
</template>

<script>
export default {}
</script>