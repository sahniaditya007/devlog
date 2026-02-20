import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, Link2, Trash2, ChevronDown } from 'lucide-react'
import { decisionsApi } from '../api/decisions'
import StatusBadge from '../components/StatusBadge'
import type { Decision, DecisionStatus, LinkType } from '../types'

const TRANSITIONS: Record<DecisionStatus, DecisionStatus[]> = {
  proposed: ['accepted', 'deprecated'],
  accepted: ['deprecated', 'superseded'],
  deprecated: [],
  superseded: [],
}

const LINK_TYPES: LinkType[] = ['supersedes', 'relates_to', 'blocked_by']

export default function DecisionDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const decisionId = Number(id)

  const [decision, setDecision] = useState<Decision | null>(null)
  const [loading, setLoading] = useState(true)
  const [transitioning, setTransitioning] = useState(false)
  const [linkTargetId, setLinkTargetId] = useState('')
  const [linkType, setLinkType] = useState<LinkType>('relates_to')
  const [linkError, setLinkError] = useState('')
  const [addingLink, setAddingLink] = useState(false)

  useEffect(() => {
    decisionsApi.get(decisionId)
      .then(setDecision)
      .finally(() => setLoading(false))
  }, [decisionId])

  const handleTransition = async (newStatus: DecisionStatus) => {
    if (!decision) return
    setTransitioning(true)
    try {
      const updated = await decisionsApi.transition(decisionId, newStatus)
      setDecision(updated)
    } finally {
      setTransitioning(false)
    }
  }

  const handleAddLink = async (e: React.FormEvent) => {
    e.preventDefault()
    setLinkError('')
    const targetId = parseInt(linkTargetId)
    if (!targetId) { setLinkError('Enter a valid decision ID.'); return }
    setAddingLink(true)
    try {
      const updated = await decisionsApi.addLink(decisionId, targetId, linkType)
      setDecision(updated)
      setLinkTargetId('')
    } catch {
      setLinkError('Could not add link. Check the decision ID and try again.')
    } finally {
      setAddingLink(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Delete this decision?')) return
    await decisionsApi.delete(decisionId)
    navigate(`/projects/${decision?.project_id}`)
  }

  if (loading) return <div className="text-center py-16 text-gray-400">Loading…</div>
  if (!decision) return <div className="text-center py-16 text-gray-500">Decision not found.</div>

  const allowedTransitions = TRANSITIONS[decision.status]

  return (
    <div className="max-w-3xl">
      <div className="flex items-center gap-3 mb-6">
        <Link to={`/projects/${decision.project_id}`} className="text-gray-400 hover:text-gray-600">
          <ArrowLeft size={18} />
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <StatusBadge status={decision.status} />
            {decision.tags.map((tag) => (
              <span key={tag} className="px-2 py-0.5 rounded-full text-xs bg-brand-50 text-brand-700">{tag}</span>
            ))}
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mt-1">{decision.title}</h1>
          <p className="text-xs text-gray-400 mt-1">
            By {decision.author_name} · {new Date(decision.created_at).toLocaleDateString()}
            {decision.updated_at !== decision.created_at && ` · Updated ${new Date(decision.updated_at).toLocaleDateString()}`}
          </p>
        </div>
        <button onClick={handleDelete} className="btn-danger !py-1.5 !px-3 text-xs">
          <Trash2 size={13} /> Delete
        </button>
      </div>

      {decision.ai_summary && (
        <div className="card p-4 mb-5 bg-brand-50 border-brand-100">
          <p className="text-xs font-semibold text-brand-600 mb-1 uppercase tracking-wide">AI Summary</p>
          <p className="text-sm text-gray-700">{decision.ai_summary}</p>
        </div>
      )}

      <div className="space-y-5">
        <Section title="Context" content={decision.context} />
        <Section title="Decision" content={decision.decision_text} />
        {decision.consequences && <Section title="Consequences" content={decision.consequences} />}
      </div>

      {allowedTransitions.length > 0 && (
        <div className="card p-4 mt-6">
          <p className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-1.5">
            <ChevronDown size={15} /> Transition Status
          </p>
          <div className="flex gap-2 flex-wrap">
            {allowedTransitions.map((s) => (
              <button
                key={s}
                onClick={() => handleTransition(s)}
                disabled={transitioning}
                className="btn-secondary !py-1.5 !px-3 text-xs capitalize"
              >
                Mark as {s}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="card p-4 mt-5">
        <p className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-1.5">
          <Link2 size={15} /> Decision Links
        </p>
        {decision.links.length > 0 ? (
          <ul className="space-y-2 mb-4">
            {decision.links.map((lnk) => (
              <li key={lnk.id} className="flex items-center gap-2 text-sm">
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${lnk.direction === 'outgoing' ? 'bg-blue-50 text-blue-700' : 'bg-purple-50 text-purple-700'}`}>
                  {lnk.direction === 'outgoing' ? '→' : '←'} {lnk.link_type.replace('_', ' ')}
                </span>
                <Link to={`/decisions/${lnk.related_id}`} className="text-brand-600 hover:underline">
                  {lnk.related_title || `Decision #${lnk.related_id}`}
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-gray-400 mb-4">No links yet.</p>
        )}
        <form onSubmit={handleAddLink} className="flex gap-2 flex-wrap items-end">
          <div>
            <label className="label text-xs">Decision ID</label>
            <input
              className="input w-28"
              type="number"
              placeholder="e.g. 42"
              value={linkTargetId}
              onChange={(e) => setLinkTargetId(e.target.value)}
            />
          </div>
          <div>
            <label className="label text-xs">Link type</label>
            <select className="input w-auto" value={linkType} onChange={(e) => setLinkType(e.target.value as LinkType)}>
              {LINK_TYPES.map((t) => <option key={t} value={t}>{t.replace('_', ' ')}</option>)}
            </select>
          </div>
          <button type="submit" className="btn-secondary !py-2" disabled={addingLink}>
            {addingLink ? 'Adding…' : 'Add Link'}
          </button>
        </form>
        {linkError && <p className="text-xs text-red-600 mt-2">{linkError}</p>}
      </div>
    </div>
  )
}

function Section({ title, content }: { title: string; content: string }) {
  return (
    <div className="card p-4">
      <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">{title}</h3>
      <p className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">{content}</p>
    </div>
  )
}
