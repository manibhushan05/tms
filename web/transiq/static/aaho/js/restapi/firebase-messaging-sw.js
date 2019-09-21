importScripts('/static/vendor/firebase/firebase-app.js');
importScripts('/static/vendor/firebase/firebase-messaging.js');
var config = {
  apiKey: "AIzaSyDSy8iWOJy1K8ZawjwbEEYi8Iy_v-FJatI",
  authDomain: "aaho-sales.firebaseapp.com",
  databaseURL: "https://aaho-sales.firebaseio.com",
  projectId: "aaho-sales",
  storageBucket: "aaho-sales.appspot.com",
  messagingSenderId: "904227386738"
};
firebase.initializeApp(config);

const messaging = firebase.messaging();

messaging.setBackgroundMessageHandler(function(payload) {
  var notificationTitle =payload.data.title;
  const notificationOptions = {
    body: payload.data.body,
    icon: '/static/aaho/images/logo/logo.png'
  };

  self.clients.matchAll({includeUncontrolled: true}).then(function (clients) {
    clients.forEach(function(client) {
        client.postMessage(payload);
    })
  })

  return self.registration.showNotification(notificationTitle,
    notificationOptions);
    
});


