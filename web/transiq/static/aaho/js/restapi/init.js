
importScripts('https://www.gstatic.com/firebasejs/5.4.1/firebase.js');
importScripts('https://www.gstatic.com/firebasejs/5.4.1/firebase-messaging.js');

var config = {
    apiKey: "AIzaSyBcMrICj3X-v6xQ3a6GVdX-PYufszbQ3Vg",
    authDomain: "my-project-d085e.firebaseapp.com",
    databaseURL: "https://my-project-d085e.firebaseio.com",
    projectId: "my-project-d085e",
    storageBucket: "my-project-d085e.appspot.com",
    messagingSenderId: "549612147166"
  };
  firebase.initializeApp(config);
  const messaging = firebase.messaging();
  messaging.requestPermission()
      .then(function () {
          console.log('Have permission');
          return messaging.getToken();
      })
      .then(function (token) {
          console.log(token);
      })