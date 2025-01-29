self.addEventListener('push', function(event) {
    const payload = event.data.json();
    const options = {
        body: payload.body,
        icon: '/static/images/icon.png',
        data: {
            url: payload.url
        }
    };
    event.waitUntil(
        self.registration.showNotification(payload.head, options)
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data.url)
    );
});