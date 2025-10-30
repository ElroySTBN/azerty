import { useNavigate } from 'react-router-dom'
import './GuaranteesPage.css'

function GuaranteesPage() {
  const navigate = useNavigate()

  return (
    <div className="container guarantees-page">
      <div className="page-header">
        <button className="btn-back" onClick={() => navigate('/')}>
          ← Retour
        </button>
        <h2>🛡️ Garanties</h2>
      </div>

      <div className="guarantee-section card">
        <h3>✅ Nos garanties</h3>
        <div className="guarantee-items">
          <div className="guarantee-item">
            <span className="guarantee-icon">🌍</span>
            <div>
              <strong>Avis 100% authentiques</strong>
              <p className="text-hint">Comptes vérifiés, IP réelles, géolocalisation précise</p>
            </div>
          </div>
          <div className="guarantee-item">
            <span className="guarantee-icon">⏰</span>
            <div>
              <strong>Livraison garantie</strong>
              <p className="text-hint">48-72h pour les avis, 24-48h pour les messages forum</p>
            </div>
          </div>
          <div className="guarantee-item">
            <span className="guarantee-icon">🔄</span>
            <div>
              <strong>Remplacement gratuit</strong>
              <p className="text-hint">Si un avis est supprimé sous 30 jours</p>
            </div>
          </div>
          <div className="guarantee-item">
            <span className="guarantee-icon">💰</span>
            <div>
              <strong>Satisfaction ou remboursement</strong>
              <p className="text-hint">Garantie satisfait ou remboursé pendant 7 jours</p>
            </div>
          </div>
          <div className="guarantee-item">
            <span className="guarantee-icon">🤝</span>
            <div>
              <strong>Support 24/7</strong>
              <p className="text-hint">Équipe réactive disponible à tout moment</p>
            </div>
          </div>
        </div>
      </div>

      <div className="guarantee-section card">
        <h3>🔒 Sécurité & Anonymat</h3>
        <div className="guarantee-items">
          <div className="guarantee-item">
            <span className="guarantee-icon">🔐</span>
            <div>
              <strong>Anonymat total</strong>
              <p className="text-hint">Aucun lien entre vous et les avis postés</p>
            </div>
          </div>
          <div className="guarantee-item">
            <span className="guarantee-icon">🗑️</span>
            <div>
              <strong>Zéro données personnelles</strong>
              <p className="text-hint">Nous ne stockons que votre ID Telegram</p>
            </div>
          </div>
          <div className="guarantee-item">
            <span className="guarantee-icon">🌐</span>
            <div>
              <strong>IP réelles uniquement</strong>
              <p className="text-hint">Pas de VPN, pas de proxies détectables</p>
            </div>
          </div>
          <div className="guarantee-item">
            <span className="guarantee-icon">✅</span>
            <div>
              <strong>Comptes vérifiés</strong>
              <p className="text-hint">Profils authentiques avec historique</p>
            </div>
          </div>
          <div className="guarantee-item">
            <span className="guarantee-icon">💳</span>
            <div>
              <strong>Paiement crypto sécurisé</strong>
              <p className="text-hint">Transactions intraçables et anonymes</p>
            </div>
          </div>
        </div>
      </div>

      <div className="guarantee-section card">
        <h3>💳 Moyens de paiement</h3>
        <div className="payment-methods">
          <div className="payment-item">
            <span className="payment-icon">₿</span>
            <strong>Bitcoin (BTC)</strong>
          </div>
          <div className="payment-item">
            <span className="payment-icon">Ξ</span>
            <strong>Ethereum (ETH)</strong>
          </div>
          <div className="payment-item">
            <span className="payment-icon">₮</span>
            <strong>USDT (TRC20/ERC20)</strong>
          </div>
          <div className="payment-item">
            <span className="payment-icon">💎</span>
            <strong>Autres cryptos sur demande</strong>
          </div>
        </div>
      </div>

      <div className="cta-section">
        <button className="btn btn-primary" onClick={() => navigate('/')}>
          📝 Passer une commande
        </button>
        <button className="btn btn-ghost" onClick={() => navigate('/support')}>
          💬 Questions ? Contactez-nous
        </button>
      </div>
    </div>
  )
}

export default GuaranteesPage

