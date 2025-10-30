import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import axios from 'axios'
import './OrdersListPage.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8081'

function OrdersListPage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [orders, setOrders] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchOrders()
  }, [])

  const fetchOrders = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/orders/${user.client_id}`)
      setOrders(response.data.orders || [])
    } catch (error) {
      console.error('Fetch orders error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusBadge = (status) => {
    const statusMap = {
      'pending': { emoji: '⏳', text: 'En attente', class: 'badge-warning' },
      'paid': { emoji: '✅', text: 'Payé', class: 'badge-success' },
      'distributed': { emoji: '🔄', text: 'En cours', class: 'badge-info' },
      'completed': { emoji: '✅', text: 'Livré', class: 'badge-success' },
      'cancelled': { emoji: '❌', text: 'Annulée', class: 'badge-warning' }
    }
    return statusMap[status] || { emoji: '❓', text: status, class: '' }
  }

  const getOrderTypeInfo = (orderType) => {
    if (orderType === 'forum') {
      return { emoji: '💬', text: 'Messages forum', class: 'badge-purple' }
    }
    return { emoji: '⭐', text: 'Avis', class: 'badge-info' }
  }

  if (isLoading) {
    return (
      <div className="container">
        <div className="loading">
          <div className="spinner"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="container orders-list-page">
      <div className="page-header">
        <button className="btn-back" onClick={() => navigate('/')}>
          ← Retour
        </button>
        <h2>📦 Mes commandes</h2>
      </div>

      {orders.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📦</div>
          <h3>Aucune commande</h3>
          <p className="text-hint">Vous n'avez pas encore passé de commande.</p>
          <button className="btn btn-primary" onClick={() => navigate('/')}>
            Passer une commande
          </button>
        </div>
      ) : (
        <div className="orders-list">
          {orders.map((order) => {
            const statusInfo = getStatusBadge(order.status)
            const typeInfo = getOrderTypeInfo(order.order_type)
            
            return (
              <div key={order.order_id} className="order-card card animate-slide-up">
                <div className="order-header">
                  <div className="order-id">
                    <strong>{order.order_id}</strong>
                    <div className="order-badges">
                      <span className={`badge ${typeInfo.class}`}>
                        {typeInfo.emoji} {typeInfo.text}
                      </span>
                      <span className={`badge ${statusInfo.class}`}>
                        {statusInfo.emoji} {statusInfo.text}
                      </span>
                    </div>
                  </div>
                  <div className="order-price">
                    <strong>{order.price.toFixed(2)} USDT</strong>
                  </div>
                </div>

                <div className="order-details">
                  <div className="detail-item">
                    <span className="text-hint">Plateforme</span>
                    <span>{order.platform}</span>
                  </div>
                  <div className="detail-item">
                    <span className="text-hint">Quantité</span>
                    <span>{order.quantity} {order.order_type === 'forum' ? 'messages' : 'avis'}</span>
                  </div>
                  <div className="detail-item">
                    <span className="text-hint">Date</span>
                    <span>{new Date(order.created_at).toLocaleDateString('fr-FR')}</span>
                  </div>
                </div>

                {order.status === 'pending' && (
                  <div className="order-actions">
                    <button className="btn btn-ghost" style={{fontSize: '0.9rem', padding: '0.5rem 1rem'}}>
                      💳 Voir instructions de paiement
                    </button>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      <div className="page-actions">
        <button className="btn btn-ghost" onClick={() => navigate('/support')}>
          💬 Contacter le support
        </button>
      </div>
    </div>
  )
}

export default OrdersListPage

