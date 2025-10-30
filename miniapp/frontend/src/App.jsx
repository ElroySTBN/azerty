import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import HomePage from './pages/HomePage'
import OrderReviewsPage from './pages/OrderReviewsPage'
import OrderForumPage from './pages/OrderForumPage'
import OrdersListPage from './pages/OrdersListPage'
import SupportPage from './pages/SupportPage'
import GuaranteesPage from './pages/GuaranteesPage'
import { useAuthStore } from './store/authStore'
import './App.css'

function App() {
  const { initAuth, isLoading, user } = useAuthStore()

  useEffect(() => {
    // Initialiser l'authentification Telegram
    initAuth()
  }, [initAuth])

  if (isLoading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="container">
        <div className="error-container">
          <h2>⚠️ Erreur d'authentification</h2>
          <p className="text-hint">
            Cette application doit être ouverte depuis Telegram.
          </p>
        </div>
      </div>
    )
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/order/reviews" element={<OrderReviewsPage />} />
        <Route path="/order/forum" element={<OrderForumPage />} />
        <Route path="/orders" element={<OrdersListPage />} />
        <Route path="/support" element={<SupportPage />} />
        <Route path="/guarantees" element={<GuaranteesPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App

