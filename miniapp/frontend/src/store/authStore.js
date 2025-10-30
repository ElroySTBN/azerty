import { create } from 'zustand'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8081'

export const useAuthStore = create((set) => ({
  user: null,
  isLoading: true,
  error: null,

  initAuth: async () => {
    try {
      const tg = window.Telegram?.WebApp
      
      if (!tg || !tg.initData) {
        set({ isLoading: false, error: 'Not in Telegram' })
        return
      }

      // Envoyer initData au backend pour validation
      const response = await axios.post(`${API_URL}/api/auth`, {
        initData: tg.initData,
        user: tg.initDataUnsafe?.user
      })

      if (response.data.success) {
        set({
          user: response.data.user,
          isLoading: false,
          error: null
        })
      } else {
        set({ isLoading: false, error: 'Auth failed' })
      }
    } catch (error) {
      console.error('Auth error:', error)
      set({ isLoading: false, error: error.message })
    }
  },

  logout: () => {
    set({ user: null })
  }
}))

