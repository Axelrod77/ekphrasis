import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../api/client'
import toast from 'react-hot-toast'

export function useTaxHarvestSummary() {
  return useQuery({
    queryKey: ['tax-harvest'],
    queryFn: async () => {
      const { data } = await api.get('/tax-harvest/summary')
      return data
    },
  })
}

export function useAnalyzeTaxHarvest() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => api.post('/tax-harvest/analyze'),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['tax-harvest'] })
      toast.success('Analysis complete')
    },
  })
}

export function useUpdateRecommendation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      api.patch(`/tax-harvest/recommendations/${id}`, { status }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['tax-harvest'] })
    },
  })
}
