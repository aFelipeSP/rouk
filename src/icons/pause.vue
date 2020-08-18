<template>
  <svg style="display:block" viewBox="0 0 1 1"
    preserveAspectRatio="none" @click="$emit('click', $emit)"
    stroke="currentColor" stroke-width="0.25"
  >
    <line x1="0.25" y1="0.05" x2="0.25" y2="0.95" />
    <line x1="0.75" y1="0.05" x2="0.75" y2="0.95" />  
  </svg>
</template>

<script>
export default {}
</script>