import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../api/client'
import toast from 'react-hot-toast'

export function useMFHoldings() {
  return useQuery({
    queryKey: ['mf-holdings'],
    queryFn: async () => {
      const { data } = await api.get('/mutual-funds/holdings')
      return data
    },
  })
}

export function useMFAnalysis() {
  return useQuery({
    queryKey: ['mf-analysis'],
    queryFn: async () => {
      const { data } = await api.get('/mutual-funds/analysis')
      return data
    },
  })
}

export function useUploadCAS() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      return api.post('/mutual-funds/upload-cas', formData)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['mf-holdings'] })
      qc.invalidateQueries({ queryKey: ['mf-analysis'] })
      toast.success('CAS imported successfully')
    },
    onError: () => toast.error('Failed to parse CAS PDF'),
  })
}
