import http from '@/plugins/http'
import type { CorrelationResponse } from '@/types/entities/ORANGE'

// TODO: typing
export function getCorrelations(params: { size: number; app_id?: string; kpi_name?: string }) {
  return http.get<CorrelationResponse>('cab_correlation/api/v1/correlation', {
    params
  })
}
