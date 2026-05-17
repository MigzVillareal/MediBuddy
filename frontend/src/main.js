import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import  './assets/main.css'

window.OneSignalDeferred = window.OneSignalDeferred || []
OneSignalDeferred.push(async function(OneSignal) {
    await OneSignal.init({
        appId: "YOUR_APP_ID",
    })
})

createApp(App).use(router).mount("#app");

