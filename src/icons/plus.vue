<template>
  <svg style="display:block" viewBox="-0.15 -0.15 1.3 1.3" stroke="currentColor"
    preserveAspectRatio="none" stroke-width="0.25" @click="$emit('click', $emit)"
  >
    <line x1=0 y1=0.5 x2=1 y2=0.5 />
    <line x1=0.5 y1=0 x2=0.5 y2=1 />
  </svg>
</template>

<script>
export default {
}
</script>

<style>

</style>