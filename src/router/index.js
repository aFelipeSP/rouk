import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import Library from '../views/Library.vue'
import Player from '../views/Player.vue'

Vue.use(VueRouter)

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/library', name: 'library', component: Library },
  { path: '/player', name: 'player', component: Player }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
