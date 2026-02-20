import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Plus } from 'lucide-react'
import { projectsApi } from '../api/projects'
import { decisionsApi } from '../api/decisions'
import DecisionCard from '../components/DecisionCard'
import type { Project, Decision, DecisionStatus } from '../types'
import NewDecisionModal from '../components/NewDecisionModal'

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>()
  const projectId = Number(id)

  const [project, setProject] = useState<Project | null>(null)
  const [decisions, setDecisions] = useState<Decision[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [search, setSearch] = useState('')

  const load = async () => {
    const [p, d] = await Promise.all([
      projectsApi.get(projectId),
      decisionsApi.list({ project_id: projectId }),
    ])
    setProject(p)
    setDecisions(d)
    setLoading(false)
  }

  useEffect(() => { load() }, [projectId])

  const filtered = decisions.filter((d) => {
    if (statusFilter && d.status !== statusFilter) return false
    if (search && !d.title.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  const statuses: DecisionStatus[] = ['proposed', 'accepted', 'deprecated', 'superseded']

  if (loading) return <div className="text-center py-16 text-gray-400">Loading…</div>
  if (!project) return <div className="text-center py-16 text-gray-500">Project not found.</div>

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <Link to="/projects" className="text-gray-400 hover:text-gray-600">
          <ArrowLeft size={18} />
        </Link>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-900">{project.name}</h1>
          {project.description && <p className="text-sm text-gray-500 mt-0.5">{project.description}</p>}
        </div>
        <button className="btn-primary" onClick={() => setShowModal(true)}>
          <Plus size={16} /> Log Decision
        </button>
      </div>

      <div className="flex gap-3 mb-5 flex-wrap">
        <input
          className="input max-w-xs"
          placeholder="Search decisions…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className="input w-auto"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">All statuses</option>
          {statuses.map((s) => (
            <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
          ))}
        </select>
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          {decisions.length === 0 ? 'No decisions logged yet.' : 'No decisions match your filters.'}
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((d) => <DecisionCard key={d.id} decision={d} />)}
        </div>
      )}

      {showModal && (
        <NewDecisionModal
          projectId={projectId}
          onClose={() => setShowModal(false)}
          onCreated={(d) => { setDecisions([d, ...decisions]); setShowModal(false) }}
        />
      )}
    </div>
  )
}
