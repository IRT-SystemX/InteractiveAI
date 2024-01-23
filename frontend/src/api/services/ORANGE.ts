import http from '@/plugins/http'

export function getCorrelations(params: { size: number; app_id?: string; kpi_name?: string }) {
  return http.get('cab_correlation/api/v1/correlation', {
    params
  })
}
