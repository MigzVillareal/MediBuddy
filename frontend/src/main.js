import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import  './assets/main.css'

window.OneSignalDeferred = window.OneSignalDeferred || []
OneSignalDeferred.push(async function(OneSignal) {
    await OneSignal.init({
        appId: "6c085cb1-19d4-42fa-8a98-35eb7367f422",
    })
})

createApp(App).use(router).mount("#app");

