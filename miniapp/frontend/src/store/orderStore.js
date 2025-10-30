import { create } from 'zustand'

export const useOrderStore = create((set) => ({
  orderType: null, // 'reviews' or 'forum'
  formData: {
    platform: '',
    quantity: 5,
    targetLink: '',
    forumSubject: '',
    contentGeneration: false,
    instructions: ''
  },

  setOrderType: (type) => set({ orderType: type }),
  
  updateFormData: (data) => set((state) => ({
    formData: { ...state.formData, ...data }
  })),

  resetForm: () => set({
    orderType: null,
    formData: {
      platform: '',
      quantity: 5,
      targetLink: '',
      forumSubject: '',
      contentGeneration: false,
      instructions: ''
    }
  }),

  calculatePrice: () => {
    const state = useOrderStore.getState()
    const basePrice = state.formData.quantity * 5.0
    const generationFee = state.formData.contentGeneration ? state.formData.quantity * 0.5 : 0
    return basePrice + generationFee
  }
}))

