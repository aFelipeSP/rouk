<template>
  <svg style="display:block" viewBox="-0.1 -0.1 1.2 1.2" stroke="currentColor"
    preserveAspectRatio="none" fill="currentColor" @click="$emit('click', $emit)"
  >
    <defs>
      <marker id="arrowhead" markerWidth="1.5" markerHeight="2.4" 
        refX="0.8" refY="1.2" orient="auto" stroke="none"
      >
        <polygon points="0 0, 1.5 1.2, 0 2.4" />
      </marker>
    </defs>
    <path d="M1 0.5A0.5 0.5 0 1 1 0.95 0.282" fill="none" stroke-width="0.2"
      marker-end="url(#arrowhead)" stroke-linejoin="round"
    />
  </svg>
</template>

<script>
export default {}
</script>

