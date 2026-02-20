export interface User {
  id: number
  email: string
  name: string
  created_at: string
}

export interface Project {
  id: number
  name: string
  description: string | null
  owner_id: number
  created_at: string
  updated_at: string
  decision_count: number
}

export type DecisionStatus = 'proposed' | 'accepted' | 'deprecated' | 'superseded'

export type LinkType = 'supersedes' | 'relates_to' | 'blocked_by'

export interface DecisionLink {
  id: number
  direction: 'outgoing' | 'incoming'
  link_type: LinkType
  related_id: number
  related_title: string | null
}

export interface Decision {
  id: number
  title: string
  context: string
  decision_text: string
  consequences: string | null
  tags: string[]
  ai_summary: string | null
  status: DecisionStatus
  project_id: number
  author_id: number
  author_name: string | null
  created_at: string
  updated_at: string
  links: DecisionLink[]
}

export interface ApiError {
  error?: string
  errors?: Record<string, string[]>
}
