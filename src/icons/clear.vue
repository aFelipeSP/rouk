<template>
  <svg style="display:block" viewBox="-0.2 -0.2 1.4 1.4"
    preserveAspectRatio="none" stroke-width="0.25"
    stroke="currentColor" fill="none" @click="$emit('click', $emit)"
  >
    <path d="M0 0L1 1" />
    <path d="M0 1L1 0" />
  </svg>
</template>

<script>
export default {
}
</script>

<style>

</style>