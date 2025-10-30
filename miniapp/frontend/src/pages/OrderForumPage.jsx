import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useOrderStore } from '../store/orderStore'
import { useAuthStore } from '../store/authStore'
import axios from 'axios'
import './OrderPage.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8081'

function OrderForumPage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { formData, updateFormData, calculatePrice } = useOrderStore()
  
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async () => {
    if (isSubmitting) return
    
    setIsSubmitting(true)
    
    try {
      const orderData = {
        user_id: user.telegram_id,
        order_type: 'forum',
        platform: '💬 Messages Forum',
        quantity: formData.quantity,
        target_link: formData.targetLink,
        forum_subject: formData.forumSubject,
        content_generation: formData.contentGeneration,
        instructions: formData.instructions
      }

      const response = await axios.post(`${API_URL}/api/orders`, orderData)
      
      if (response.data.success) {
        window.Telegram?.WebApp?.showAlert(
          `✅ Commande créée !\n\nRéférence : ${response.data.order_id}\n\nVous allez être redirigé vers le paiement.`,
          () => navigate('/orders')
        )
      }
    } catch (error) {
      console.error('Order error:', error)
      window.Telegram?.WebApp?.showAlert('❌ Erreur lors de la création de la commande')
    } finally {
      setIsSubmitting(false)
    }
  }

  const price = calculatePrice()

  return (
    <div className="container order-page">
      <div className="page-header">
        <button className="btn-back" onClick={() => navigate('/')}>
          ← Retour
        </button>
        <h2>💬 Messages sur forums</h2>
      </div>

      <div className="form-container">
        {/* Étape 1: Quantité */}
        <div className="form-section">
          <label>
            Nombre de messages *
            <span className="text-hint"> (étape 1/4)</span>
          </label>
          <div className="quantity-selector">
            <button
              type="button"
              className="btn-qty"
              onClick={() => formData.quantity > 1 && updateFormData({ quantity: formData.quantity - 1 })}
            >
              −
            </button>
            <input
              type="number"
              value={formData.quantity}
              onChange={(e) => updateFormData({ quantity: parseInt(e.target.value) || 1 })}
              min="1"
            />
            <button
              type="button"
              className="btn-qty"
              onClick={() => updateFormData({ quantity: formData.quantity + 1 })}
            >
              +
            </button>
          </div>
        </div>

        {/* Étape 2: URL du forum */}
        {formData.quantity > 0 && (
          <div className="form-section animate-slide-up">
            <label>
              URL du forum/topic *
              <span className="text-hint"> (étape 2/4)</span>
            </label>
            <input
              type="url"
              placeholder="https://forum.example.com/..."
              value={formData.targetLink}
              onChange={(e) => updateFormData({ targetLink: e.target.value })}
            />
            <small className="text-hint">
              L'URL du forum où poster les messages
            </small>
          </div>
        )}

        {/* Étape 3: Sujet */}
        {formData.targetLink && (
          <div className="form-section animate-slide-up">
            <label>
              Sujet / Contexte *
              <span className="text-hint"> (étape 3/4)</span>
            </label>
            <textarea
              placeholder="Ex: Promotion d'un produit, témoignage client, question technique..."
              value={formData.forumSubject}
              onChange={(e) => updateFormData({ forumSubject: e.target.value })}
              rows="3"
            />
          </div>
        )}

        {/* Étape 4: Génération de contenu */}
        {formData.forumSubject && (
          <div className="form-section animate-slide-up">
            <label>
              Qui rédige les messages ?
              <span className="text-hint"> (étape 4/4)</span>
            </label>
            
            <div className="content-options">
              <button
                type="button"
                className={`content-option ${!formData.contentGeneration ? 'active' : ''}`}
                onClick={() => updateFormData({ contentGeneration: false })}
              >
                <div className="option-icon">📝</div>
                <div className="option-content">
                  <strong>Je rédige moi-même</strong>
                  <small className="text-hint">Vous fournissez le contenu</small>
                  <strong className="option-price">{formData.quantity * 5} USDT</strong>
                </div>
              </button>

              <button
                type="button"
                className={`content-option ${formData.contentGeneration ? 'active' : ''}`}
                onClick={() => updateFormData({ contentGeneration: true })}
              >
                <div className="option-icon">🤖</div>
                <div className="option-content">
                  <strong>Le Bon Mot rédige ✨</strong>
                  <small className="text-hint">Messages authentiques et variés</small>
                  <strong className="option-price">{price.toFixed(2)} USDT</strong>
                  <span className="badge badge-info">+0.50 USDT/message</span>
                </div>
              </button>
            </div>

            {formData.contentGeneration && (
              <div className="form-section animate-slide-up">
                <label>Instructions (optionnel)</label>
                <textarea
                  placeholder="Ton souhaité, points à mentionner, mots-clés, style d'écriture..."
                  value={formData.instructions}
                  onChange={(e) => updateFormData({ instructions: e.target.value })}
                />
              </div>
            )}
          </div>
        )}

        {/* Récapitulatif et submit */}
        {formData.forumSubject && (
          <div className="form-section recap-section animate-slide-up">
            <div className="divider"></div>
            <h3>📋 Récapitulatif</h3>
            <div className="recap-details">
              <div className="recap-item">
                <span className="text-hint">Type</span>
                <strong>💬 Messages Forum</strong>
              </div>
              <div className="recap-item">
                <span className="text-hint">Nombre de messages</span>
                <strong>{formData.quantity}</strong>
              </div>
              <div className="recap-item">
                <span className="text-hint">Génération</span>
                <strong>{formData.contentGeneration ? 'Oui ✨' : 'Non'}</strong>
              </div>
              <div className="recap-item">
                <span className="text-hint">Délai de livraison</span>
                <strong>24-48h</strong>
              </div>
              <div className="recap-item total">
                <span>Prix total</span>
                <strong className="price-large">{price.toFixed(2)} USDT</strong>
              </div>
            </div>

            <button
              className="btn btn-primary"
              onClick={handleSubmit}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Création...' : '✅ Confirmer et payer'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default OrderForumPage

