import Vue from 'vue'
import VueRouter from 'vue-router'
// TODO: Move diseases and lifetables into components and put them both on home. Get rid of nav.
//import Home from '../views/Home.vue'
import Diseases from '../views/Diseases.vue'
import LifeTables from '../views/LifeTables'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Diseases',
    component: Diseases
  },
  {
    path: '/diseases',
    name: 'Diseases',
    component: Diseases
  },
  {
    path: '/lifetables',
    name: 'LifeTables',
    component: LifeTables
  },
]

const router = new VueRouter({
  routes
})

export default router
