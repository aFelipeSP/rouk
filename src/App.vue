<template>
  <div id="app">
    <div style="flex: 1;overflow: auto">
      <router-view/>
    </div>
    <div style="display:flex;align-items:center;background-color:#dddddd">
      <div
        v-text="'Home'"
        class="nav-btn"
        @click="$router.push({name: 'home'})"
        :style="$route.name === 'home' ? 'font-weight:bold' : ''"
      />
      <div
        v-text="'Search'"
        class="nav-btn"
        @click="$router.push({name: 'search'})"
        :style="$route.name === 'search' ? 'font-weight:bold' : ''"
      />
      <div
        v-text="'Library'"
        class="nav-btn"
        @click="$router.push({name: 'library'})"
        :style="$route.name === 'library' ? 'font-weight:bold' : ''"
      />
    </div>
  </div>
</template>

<style>
html, body {
  height: 100%;
  width: 100%;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #374f68;
  display: flex;
  flex-direction: column;
  height: 100%;
}

#nav-btn {
  font-size: 110%;
}

#r-title {
  font-size: 105%;
  font-weight: bold;
}

</style>
