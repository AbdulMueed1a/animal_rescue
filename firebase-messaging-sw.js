importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging-compat.js');

const firebaseConfig = {
  apiKey: "AIzaSyA80SmOpP14bbtiVj2OA363_Cp8Hm0_W50",
  authDomain: "animal-rescue-portal.firebaseapp.com",
  projectId: "animal-rescue-portal",
  storageBucket: "animal-rescue-portal.firebasestorage.app",
  messagingSenderId: "833958160499",
  appId: "1:833958160499:web:3e651a4a2bbf1f76692206"
};
firebase.initializeApp(firebaseConfig);
const messaging = firebase.messaging();

// Background message handler
messaging.onBackgroundMessage((payload) => {
  console.log('Background message:', payload);
  return self.registration.showNotification(
    payload.notification.title,
    {
      body: payload.notification.body,
      data: payload.data
    }
  );
});