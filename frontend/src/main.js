import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/main.css'

window.OneSignalDeferred = window.OneSignalDeferred || []
OneSignalDeferred.push(async function(OneSignal) {
    await OneSignal.init({
        appId: "your-actual-app-id",
        notifyButton: {
            enable: true,
        },
        serviceWorkerPath: "/OneSignalSDKWorker.js",
    })
})

if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/OneSignalSDKWorker.js')
        .then(reg => console.log('SW registered:', reg))
        .catch(err => console.log('SW registration failed:', err))
}

createApp(App).use(router).mount("#app")