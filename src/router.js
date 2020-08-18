import Vue from 'vue'
import VueRouter from 'vue-router'
import MainLayout from '@/layouts/MainLayout'
import Library from '@/views/Library.vue'
import NotFound from '@/views/NotFound.vue'
import Album from '@/views/Album.vue'
import Artist from '@/views/Artist.vue'
import Playlist from '@/views/Playlist.vue'
import Song from '@/views/Song.vue'

Vue.use(VueRouter)

const routes = [
  { path: '/static', redirect: {name: 'library'} }, 
  { path: '/', redirect: {name: 'library'} },
  { path: '/', component: MainLayout, children: [
    { name: 'home', path: '/', redirect: {name: 'library'} },
    { path: '/library', name: 'library', component: Library },
    { path: '/album/:id', name: 'album', component: Album },
    { path: '/artist/:id', name: 'artist', component: Artist },
    { path: '/playlist/:id', name: 'playlist', component: Playlist },
    { path: '/song/:id', name: 'song', component: Song }
  ]},
  { path: '*', name: 'notFound', component: NotFound }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
