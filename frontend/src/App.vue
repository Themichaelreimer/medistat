<template>
  <v-app>
    <div id="app">
      <v-app-bar
        dense
      >
        <div id="nav">
          <span style="float:left">Medistat.online</span>
          <router-link style="float:left; padding-left:2em" to="/diseases">Diseases</router-link>
          <router-link style="float:center; padding-left:2em " to="/lifetables">Life Tables</router-link>
          <span>
            <a style="text-align: right; clear:left;" href="https://github.com/Themichaelreimer/medistat">See me on GitHub!</a>
          </span>
        </div>
      </v-app-bar>
      <router-view/>
    </div>
  </v-app>
</template>

<style>
#app {
  font-family: 'TT Ricordi Greto Trial Variable', Avenir, Helvetica, Arial, sans-serif;
  font-weight: 600;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #555555;
  background: url("/bg.png") no-repeat center center fixed;
  background-size: cover;
}

#nav {
  padding: 30px;
  width:100%;
  text-align:right;
}

#nav a {
  font-weight: bold;
  color: #5555ff;
}

#nav a.router-link-exact-active {
  color: #ff5555;
}

.glass {
  /* From https://css.glass */
  background: rgba(255, 255, 255, 0.3);
  border-radius: 16px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(13.9px);
  -webkit-backdrop-filter: blur(13.9px);
  border: 1px solid rgba(255, 255, 255, 0.11);
}
</style>
