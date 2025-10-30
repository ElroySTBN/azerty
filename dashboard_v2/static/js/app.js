// Application principale - Dashboard Mobile
class DashboardApp {
  constructor() {
    this.currentView = 'orders';
    this.orders = [];
    this.messages = [];
    this.init();
  }

  async init() {
    // Enregistrer le Service Worker
    if ('serviceWorker' in navigator) {
      try {
        await navigator.serviceWorker.register('/static/sw.js');
        console.log('✅ Service Worker registered');
      } catch (error) {
        console.error('❌ SW registration failed:', error);
      }
    }

    // Charger les données initiales
    await this.loadOrders();
    this.setupEventListeners();
    this.startAutoRefresh();
  }

  setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const view = e.currentTarget.dataset.view;
        this.switchView(view);
      });
    });

    // Pull to refresh
    let startY = 0;
    let pulling = false;

    document.addEventListener('touchstart', (e) => {
      if (window.scrollY === 0) {
        startY = e.touches[0].pageY;
        pulling = true;
      }
    });

    document.addEventListener('touchmove', (e) => {
      if (!pulling) return;
      const currentY = e.touches[0].pageY;
      const diff = currentY - startY;
      
      if (diff > 80) {
        this.refresh();
        pulling = false;
      }
    });
  }

  switchView(view) {
    this.currentView = view;
    
    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
      item.classList.toggle('active', item.dataset.view === view);
    });

    // Update content
    switch(view) {
      case 'orders':
        this.renderOrders();
        break;
      case 'messages':
        this.renderMessages();
        break;
      case 'stats':
        this.renderStats();
        break;
    }
  }

  async loadOrders() {
    try {
      const response = await fetch('/api/mobile/orders');
      const data = await response.json();
      
      if (data.success) {
        this.orders = data.orders;
        this.renderOrders();
        this.updateStats();
      }
    } catch (error) {
      console.error('Error loading orders:', error);
      this.showError('Impossible de charger les commandes');
    }
  }

  renderOrders() {
    const container = document.getElementById('orders-list');
    if (!container) return;

    if (this.orders.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">📦</div>
          <p>Aucune commande</p>
        </div>
      `;
      return;
    }

    container.innerHTML = this.orders.map(order => `
      <a href="/mobile/order/${order.order_id}" class="order-card">
        <div class="order-header">
          <span class="order-id">${order.order_id}</span>
          <span class="status-badge status-${order.status.toLowerCase().replace(' ', '-')}">
            ${this.getStatusText(order.status)}
          </span>
        </div>
        <div class="order-meta">
          <span>${this.getOrderTypeIcon(order.order_type)} ${order.quantity} ${order.order_type === 'forum' ? 'messages' : 'avis'}</span>
          <span>💰 ${order.price} USDT</span>
        </div>
        <p class="order-brief">${order.brief || 'Pas de brief'}</p>
      </a>
    `).join('');
  }

  getStatusText(status) {
    const statusMap = {
      'pending': '💰 À vérifier',
      'in_progress': '✍️ En cours',
      'completed': '✅ Terminé',
      'delivered': '📦 Livré'
    };
    return statusMap[status] || status;
  }

  getOrderTypeIcon(type) {
    return type === 'forum' ? '💬' : '⭐';
  }

  updateStats() {
    const pending = this.orders.filter(o => o.status === 'pending').length;
    const inProgress = this.orders.filter(o => o.status === 'in_progress').length;
    const today = this.orders.filter(o => this.isToday(o.created_at)).length;
    const revenue = this.orders.reduce((sum, o) => sum + parseFloat(o.price), 0);

    document.getElementById('stat-pending').textContent = pending;
    document.getElementById('stat-in-progress').textContent = inProgress;
    document.getElementById('stat-today').textContent = today;
    document.getElementById('stat-revenue').textContent = revenue.toFixed(0);
  }

  isToday(dateString) {
    const date = new Date(dateString);
    const today = new Date();
    return date.toDateString() === today.toDateString();
  }

  async renderMessages() {
    const container = document.getElementById('main-content');
    if (!container) return;

    try {
      const response = await fetch('/api/mobile/messages');
      const data = await response.json();

      if (data.success) {
        this.messages = data.messages;

        if (this.messages.length === 0) {
          container.innerHTML = `
            <div class="empty-state">
              <div class="empty-icon">💬</div>
              <p>Aucun message</p>
            </div>
          `;
          return;
        }

        container.innerHTML = `
          <div class="orders-list">
            ${this.messages.map(msg => `
              <a href="/mobile/chat/${msg.client_id}" class="order-card">
                <div class="order-header">
                  <span class="order-id">@${msg.telegram_username || msg.client_id.substring(0, 8)}</span>
                  ${msg.unread_count > 0 ? `<span class="header-badge">${msg.unread_count}</span>` : ''}
                </div>
                <p class="order-brief">${msg.last_message}</p>
                <div class="order-meta">
                  <span>${this.formatTime(msg.last_message_time)}</span>
                </div>
              </a>
            `).join('')}
          </div>
        `;
      }
    } catch (error) {
      console.error('Error loading messages:', error);
    }
  }

  formatTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'À l\'instant';
    if (minutes < 60) return `Il y a ${minutes}m`;
    if (hours < 24) return `Il y a ${hours}h`;
    return `Il y a ${days}j`;
  }

  async refresh() {
    const ptr = document.createElement('div');
    ptr.className = 'ptr';
    ptr.textContent = '🔄 Actualisation...';
    document.body.prepend(ptr);

    await this.loadOrders();

    setTimeout(() => ptr.remove(), 500);
  }

  startAutoRefresh() {
    // Rafraîchir toutes les 30 secondes
    setInterval(() => this.loadOrders(), 30000);
  }

  showError(message) {
    // TODO: Implémenter un toast/snackbar
    alert(message);
  }
}

// Initialiser l'app au chargement
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.app = new DashboardApp();
  });
} else {
  window.app = new DashboardApp();
}

