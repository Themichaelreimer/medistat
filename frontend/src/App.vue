<template>
  <v-app>
    <div id="app">
        <div id="nav" class="glass dense">
          <div class="left-nav-items">
            <span>Medistat.online</span>
            <router-link to="/diseases">Diseases</router-link>
            <router-link to="/lifetables">Life Tables</router-link>
          </div>
          <div class="right-nav-items">
            <a href="https://github.com/Themichaelreimer/medistat">See me on GitHub!</a>
          </div>
        </div>
      <router-view/>
    </div>
  </v-app>
</template>
