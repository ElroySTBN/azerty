// Gestion des notifications push
class NotificationManager {
  constructor() {
    this.permission = Notification.permission;
    this.subscription = null;
  }

  async init() {
    // Vérifier si les notifications sont supportées
    if (!('Notification' in window)) {
      console.warn('Notifications non supportées');
      return false;
    }

    // Si déjà autorisé, s'abonner
    if (this.permission === 'granted') {
      await this.subscribe();
      return true;
    }

    return false;
  }

  async requestPermission() {
    try {
      this.permission = await Notification.requestPermission();
      
      if (this.permission === 'granted') {
        await this.subscribe();
        this.showNotification(
          '🔔 Notifications activées',
          'Vous recevrez des notifications pour les nouvelles commandes'
        );
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Error requesting permission:', error);
      return false;
    }
  }

  async subscribe() {
    try {
      const registration = await navigator.serviceWorker.ready;
      
      // Vérifier si déjà abonné
      this.subscription = await registration.pushManager.getSubscription();
      
      if (!this.subscription) {
        // S'abonner aux notifications push
        this.subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: this.urlBase64ToUint8Array(
            'YOUR_VAPID_PUBLIC_KEY' // À remplacer par ta vraie clé VAPID
          )
        });

        // Envoyer la subscription au serveur
        await this.sendSubscriptionToServer(this.subscription);
      }
      
      return this.subscription;
    } catch (error) {
      console.error('Error subscribing:', error);
      return null;
    }
  }

  async sendSubscriptionToServer(subscription) {
    try {
      const response = await fetch('/api/mobile/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(subscription)
      });
      
      return await response.json();
    } catch (error) {
      console.error('Error sending subscription:', error);
    }
  }

  async showNotification(title, body, options = {}) {
    if (this.permission !== 'granted') {
      return;
    }

    try {
      const registration = await navigator.serviceWorker.ready;
      await registration.showNotification(title, {
        body,
        icon: '/static/icons/icon-192.png',
        badge: '/static/icons/badge-72.png',
        vibrate: [200, 100, 200],
        ...options
      });
    } catch (error) {
      console.error('Error showing notification:', error);
    }
  }

  urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/\-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }
}

// Initialiser le gestionnaire de notifications
window.notificationManager = new NotificationManager();
window.notificationManager.init();

