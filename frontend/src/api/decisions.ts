import client from './client'
import type { Decision, DecisionStatus, LinkType } from '../types'

export interface DecisionCreatePayload {
  title: string
  context: string
  decision_text: string
  consequences?: string
  tags?: string[]
  project_id: number
}

export interface DecisionUpdatePayload {
  title?: string
  context?: string
  decision_text?: string
  consequences?: string
  tags?: string[]
}

export const decisionsApi = {
  list: (params?: { project_id?: number; status?: string; tag?: string; q?: string }) =>
    client.get<Decision[]>('/decisions/', { params }).then((r) => r.data),

  get: (id: number) => client.get<Decision>(`/decisions/${id}`).then((r) => r.data),

  create: (payload: DecisionCreatePayload) =>
    client.post<Decision>('/decisions/', payload).then((r) => r.data),

  update: (id: number, payload: DecisionUpdatePayload) =>
    client.put<Decision>(`/decisions/${id}`, payload).then((r) => r.data),

  transition: (id: number, status: DecisionStatus) =>
    client.patch<Decision>(`/decisions/${id}/status`, { status }).then((r) => r.data),

  addLink: (id: number, target_id: number, link_type: LinkType) =>
    client.post<Decision>(`/decisions/${id}/links`, { target_id, link_type }).then((r) => r.data),

  delete: (id: number) => client.delete(`/decisions/${id}`).then((r) => r.data),
}
