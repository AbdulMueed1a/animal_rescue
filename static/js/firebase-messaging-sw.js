importScripts('https://www.gstatic.com/firebasejs/10.5.0/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/10.5.0/firebase-messaging.js');

firebase.initializeApp({
  apiKey: "AIzaSyA80SmOpP14bbtiVj2OA363_Cp8Hm0_W50",
  authDomain: "animal-rescue-portal.firebaseapp.com",
  projectId: "animal-rescue-portal",
  storageBucket: "animal-rescue-portal.firebasestorage.app",
  messagingSenderId: "833958160499",
  appId: "1:833958160499:web:3e651a4a2bbf1f76692206",
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  const { title, body, icon } = payload.notification;
  self.registration.showNotification(title, { body, icon });
});