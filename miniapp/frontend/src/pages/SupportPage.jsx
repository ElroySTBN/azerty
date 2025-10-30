import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import axios from 'axios'
import './SupportPage.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8081'

function SupportPage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [message, setMessage] = useState('')
  const [isSending, setIsSending] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!message.trim() || isSending) return

    setIsSending(true)
    
    try {
      await axios.post(`${API_URL}/api/support`, {
        client_id: user.client_id,
        telegram_username: user.username,
        message: message
      })

      window.Telegram?.WebApp?.showAlert(
        '✅ Message envoyé au support !\n\nNotre équipe vous répondra sous 2h.',
        () => {
          setMessage('')
          navigate('/')
        }
      )
    } catch (error) {
      console.error('Support error:', error)
      window.Telegram?.WebApp?.showAlert('❌ Erreur lors de l\'envoi du message')
    } finally {
      setIsSending(false)
    }
  }

  return (
    <div className="container support-page">
      <div className="page-header">
        <button className="btn-back" onClick={() => navigate('/')}>
          ← Retour
        </button>
        <h2>💬 Support</h2>
      </div>

      <div className="support-info card">
        <h3>🤝 Nous sommes là pour vous aider</h3>
        <div className="info-items">
          <div className="info-item">
            <span className="info-icon">⏱️</span>
            <div>
              <strong>Temps de réponse</strong>
              <p className="text-hint">Moins de 2 heures</p>
            </div>
          </div>
          <div className="info-item">
            <span className="info-icon">💬</span>
            <div>
              <strong>Support humain</strong>
              <p className="text-hint">Pas de bot, des vraies personnes</p>
            </div>
          </div>
          <div className="info-item">
            <span className="info-icon">🔒</span>
            <div>
              <strong>Confidentialité</strong>
              <p className="text-hint">Vos données restent anonymes</p>
            </div>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="support-form">
        <div className="form-section">
          <label>Votre message *</label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Décrivez votre problème ou votre question..."
            rows="6"
            required
          />
          <small className="text-hint">
            Incluez un numéro de commande si pertinent
          </small>
        </div>

        <button
          type="submit"
          className="btn btn-primary"
          disabled={!message.trim() || isSending}
        >
          {isSending ? 'Envoi...' : '📤 Envoyer le message'}
        </button>
      </form>

      <div className="quick-links">
        <h4>Questions fréquentes</h4>
        <button className="btn btn-secondary" type="button">
          ❓ Comment fonctionne le paiement crypto ?
        </button>
        <button className="btn btn-secondary" type="button">
          ⏰ Quel est le délai de livraison ?
        </button>
        <button className="btn btn-secondary" type="button">
          🔒 Comment est garanti l'anonymat ?
        </button>
      </div>
    </div>
  )
}

export default SupportPage

