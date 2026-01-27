import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../api/client'
import toast from 'react-hot-toast'

export function usePortfolioSummary() {
  return useQuery({
    queryKey: ['portfolio'],
    queryFn: async () => {
      const { data } = await api.get('/portfolio/summary')
      return data
    },
  })
}

export function useAddHolding() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: { stock_id: string; quantity: number; buy_price: number; buy_date: string }) =>
      api.post('/portfolio/holdings', data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['portfolio'] })
      toast.success('Holding added')
    },
    onError: () => toast.error('Failed to add holding'),
  })
}

export function useDeleteHolding() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.delete(`/portfolio/holdings/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['portfolio'] })
      toast.success('Holding deleted')
    },
  })
}
