import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../api/client'
import toast from 'react-hot-toast'

export function useWatchlist(category?: string) {
  return useQuery({
    queryKey: ['watchlist', category],
    queryFn: async () => {
      const params: Record<string, string> = {}
      if (category) params.category = category
      const { data } = await api.get('/watchlist', { params })
      return data
    },
  })
}

export function useAddToWatchlist() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: { stock_id: string; category?: string }) =>
      api.post('/watchlist', data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['watchlist'] })
      toast.success('Added to watchlist')
    },
  })
}

export function useRemoveFromWatchlist() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.delete(`/watchlist/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['watchlist'] })
      toast.success('Removed from watchlist')
    },
  })
}
