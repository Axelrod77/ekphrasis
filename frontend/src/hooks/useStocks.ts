import { useQuery } from '@tanstack/react-query'
import api from '../api/client'

interface StockFilters {
  page?: number
  pageSize?: number
  search?: string
  sector?: string
  sortBy?: string
  sortOrder?: string
  minPe?: number
  maxPe?: number
  minRoce?: number
  minRoe?: number
  minMarketCap?: number
  maxDebtToEquity?: number
}

export function useStocks(filters: StockFilters = {}) {
  return useQuery({
    queryKey: ['stocks', filters],
    queryFn: async () => {
      const params: Record<string, any> = {}
      if (filters.page) params.page = filters.page
      if (filters.pageSize) params.page_size = filters.pageSize
      if (filters.search) params.search = filters.search
      if (filters.sector) params.sector = filters.sector
      if (filters.sortBy) params.sort_by = filters.sortBy
      if (filters.sortOrder) params.sort_order = filters.sortOrder
      if (filters.minPe !== undefined) params.min_pe = filters.minPe
      if (filters.maxPe !== undefined) params.max_pe = filters.maxPe
      if (filters.minRoce !== undefined) params.min_roce = filters.minRoce
      if (filters.minRoe !== undefined) params.min_roe = filters.minRoe
      if (filters.minMarketCap !== undefined) params.min_market_cap = filters.minMarketCap
      if (filters.maxDebtToEquity !== undefined) params.max_debt_to_equity = filters.maxDebtToEquity
      const { data } = await api.get('/stocks', { params })
      return data
    },
  })
}

export function useStockDetail(symbol: string) {
  return useQuery({
    queryKey: ['stock', symbol],
    queryFn: async () => {
      const { data } = await api.get(`/stocks/${symbol}`)
      return data
    },
    enabled: !!symbol,
  })
}
