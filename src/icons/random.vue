<template>
  <svg style="display:block" viewBox="0 0 1 1" preserveAspectRatio="none"
    stroke="currentColor" fill="currentColor" @click="$emit('click', $emit)"
  >
    <defs>
      <marker id="arrowhead" markerWidth="1.5" markerHeight="2.4" 
        refX="0.25" refY="1.2" orient="auto" stroke="none"
      >
        <polygon points="0 0, 1.5 1.2, 0 2.4" />
      </marker>
    </defs>
    <path d="M0 0.3H0.25L0.65 0.7H0.81" fill="none" stroke-width="0.15"
      marker-end="url(#arrowhead)" stroke-linejoin="round"
    />
    <path d="M0 0.7H0.25L0.65 0.3H0.81" fill="none" stroke-width="0.15"
      marker-end="url(#arrowhead)" stroke-linejoin="round"
    />
  </svg>
</template>

<script>
export default {}
</script>

