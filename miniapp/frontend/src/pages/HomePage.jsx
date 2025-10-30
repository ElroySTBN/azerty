import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import './HomePage.css'

function HomePage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()

  return (
    <div className="container home-page">
      <div className="header-section animate-slide-up">
        <h1>🔐 Le Bon Mot</h1>
        <p className="subtitle">Service Anonyme de E-réputation</p>
        
        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-icon">✅</div>
            <div className="stat-text">
              <strong>15 000+</strong>
              <span className="text-hint">avis livrés</span>
            </div>
          </div>
          <div className="stat-item">
            <div className="stat-icon">⚡</div>
            <div className="stat-text">
              <strong>24-72h</strong>
              <span className="text-hint">délai moyen</span>
            </div>
          </div>
        </div>

        <div className="features-list">
          <div className="feature-item">
            <span className="feature-icon">🌍</span>
            <span>Avis 100% authentiques et géolocalisés</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">💬</span>
            <span>Messages de forum professionnels</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🔒</span>
            <span>Anonymat total garanti</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">💳</span>
            <span>Paiement crypto uniquement</span>
          </div>
        </div>

        {user && (
          <div className="user-badge">
            <span className="text-hint">Votre ID : </span>
            <strong>#{user.client_id}</strong>
          </div>
        )}
      </div>

      <div className="actions-section">
        <h3>Que souhaitez-vous commander ?</h3>
        
        <button 
          className="btn btn-primary action-card"
          onClick={() => navigate('/order/reviews')}
        >
          <span className="action-icon">⭐</span>
          <div className="action-content">
            <strong>Commander des avis</strong>
            <small className="text-hint">Google, Trustpilot, autres</small>
          </div>
        </button>

        <button 
          className="btn btn-primary action-card"
          onClick={() => navigate('/order/forum')}
        >
          <span className="action-icon">💬</span>
          <div className="action-content">
            <strong>Messages sur forums</strong>
            <small className="text-hint">Posts professionnels</small>
          </div>
        </button>

        <div className="secondary-actions">
          <button 
            className="btn btn-secondary"
            onClick={() => navigate('/orders')}
          >
            📦 Mes commandes
          </button>
          
          <button 
            className="btn btn-ghost"
            onClick={() => navigate('/guarantees')}
          >
            🛡️ Garanties
          </button>

          <button 
            className="btn btn-ghost"
            onClick={() => navigate('/support')}
          >
            💬 Support
          </button>
        </div>
      </div>
    </div>
  )
}

export default HomePage

