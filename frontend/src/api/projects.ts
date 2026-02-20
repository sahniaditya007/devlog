import client from './client'
import type { Project } from '../types'

export interface ProjectPayload { name: string; description?: string }

export const projectsApi = {
  list: () => client.get<Project[]>('/projects/').then((r) => r.data),

  get: (id: number) => client.get<Project>(`/projects/${id}`).then((r) => r.data),

  create: (payload: ProjectPayload) =>
    client.post<Project>('/projects/', payload).then((r) => r.data),

  update: (id: number, payload: Partial<ProjectPayload>) =>
    client.put<Project>(`/projects/${id}`, payload).then((r) => r.data),

  delete: (id: number) => client.delete(`/projects/${id}`).then((r) => r.data),
}
