import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/main.css'
import OneSignalVuePlugin from '@onesignal/onesignal-vue3'

const app = createApp(App)

app.use(router)
app.use(OneSignalVuePlugin, {
    appId: '6c085cb1-19d4-42fa-8a98-35eb7367f422',
    serviceWorkerParam: { scope: '/' },
    serviceWorkerPath: 'OneSignalSDKWorker.js',
    promptOptions: {
        slidedown: {
            prompts: [
                {
                    type: 'push',
                    autoPrompt: true,
                    text: {
                        actionMessage: 'Allow MediBuddy to send you medication reminders.',
                        acceptButton: 'Allow',
                        cancelButton: 'No Thanks',
                    },
                }
            ]
        }
    }
})

app.mount("#app")