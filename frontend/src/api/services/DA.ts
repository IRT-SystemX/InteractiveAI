import http from '@/plugins/http'

export function getProcedure(event_type: string = 'ENG1: AUTO SHUTDOWN') {
  return http.post('/cab_recommendation/api/v1/procedure', {
    event: {
      event_type
    }
  })
}
