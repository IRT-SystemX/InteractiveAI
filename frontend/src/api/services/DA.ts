import type { Procedure } from '@/entities/DA/types'
import http from '@/plugins/http'

export function getProcedure(event_type: string = 'ENG1: AUTO SHUTDOWN') {
  return http.post<Procedure>('/cab_recommendation/api/v1/procedure', {
    event: {
      event_type
    }
  })
}
