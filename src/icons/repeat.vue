<template>
  <svg style="display:block" viewBox="0 0 1 1" preserveAspectRatio="none"
    stroke="currentColor" fill="currentColor"
  >
    <defs>
      <marker id="arrowhead" markerWidth="1.5" markerHeight="2.4" 
        refX="0.25" refY="1.2" orient="auto" stroke="none">
        <polygon points="0 0, 1.5 1.2, 0 2.4" />
      </marker>
    </defs>
    <path d="M0.1 0.5V0.25H0.75" fill="none" stroke-width="0.2"
      marker-end="url(#arrowhead)" stroke-linejoin="round"
    />
    <path d="M0.9 0.5V0.75H0.25" fill="none" stroke-width="0.2"
      marker-end="url(#arrowhead)" stroke-linejoin="round"
    />
  </svg>
</template>

<script>
export default {}
</script>

