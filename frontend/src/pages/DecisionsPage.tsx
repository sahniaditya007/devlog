import { useState, useEffect } from 'react'
import { decisionsApi } from '../api/decisions'
import DecisionCard from '../components/DecisionCard'
import type { Decision, DecisionStatus } from '../types'

const STATUSES: DecisionStatus[] = ['proposed', 'accepted', 'deprecated', 'superseded']

export default function DecisionsPage() {
  const [decisions, setDecisions] = useState<Decision[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  useEffect(() => {
    decisionsApi.list().then(setDecisions).finally(() => setLoading(false))
  }, [])

  const filtered = decisions.filter((d) => {
    if (statusFilter && d.status !== statusFilter) return false
    if (search && !d.title.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">All Decisions</h1>
        <p className="text-sm text-gray-500 mt-0.5">Browse decisions across all your projects</p>
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
          {STATUSES.map((s) => (
            <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="text-center py-16 text-gray-400">Loading…</div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          {decisions.length === 0 ? 'No decisions yet. Create a project and log your first decision.' : 'No decisions match your filters.'}
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((d) => <DecisionCard key={d.id} decision={d} />)}
        </div>
      )}
    </div>
  )
}
