import { useState } from 'react'
import { X, Sparkles } from 'lucide-react'
import { decisionsApi } from '../api/decisions'
import type { Decision } from '../types'

interface Props {
  projectId: number
  onClose: () => void
  onCreated: (d: Decision) => void
}

export default function NewDecisionModal({ projectId, onClose, onCreated }: Props) {
  const [form, setForm] = useState({
    title: '',
    context: '',
    decision_text: '',
    consequences: '',
    tags: '',
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      const tags = form.tags
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean)
      const d = await decisionsApi.create({
        title: form.title,
        context: form.context,
        decision_text: form.decision_text,
        consequences: form.consequences || undefined,
        tags,
        project_id: projectId,
      })
      onCreated(d)
    } catch {
      setError('Failed to create decision. Please check all required fields.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-start justify-center z-50 px-4 py-8 overflow-y-auto">
      <div className="card p-6 w-full max-w-2xl my-auto">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold">Log a Decision</h2>
            <p className="text-xs text-gray-500 mt-0.5 flex items-center gap-1">
              <Sparkles size={11} className="text-brand-500" />
              AI will auto-summarize and suggest tags if no tags are provided
            </p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X size={18} />
          </button>
        </div>

        {error && <p className="text-sm text-red-600 mb-3 p-2 bg-red-50 rounded">{error}</p>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Title *</label>
            <input
              className="input"
              placeholder="e.g. Use PostgreSQL for primary data store"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              required
              autoFocus
            />
          </div>
          <div>
            <label className="label">Context * <span className="text-gray-400 font-normal">(What problem are you solving?)</span></label>
            <textarea
              className="input resize-none"
              rows={3}
              placeholder="Describe the situation and forces at play…"
              value={form.context}
              onChange={(e) => setForm({ ...form, context: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="label">Decision * <span className="text-gray-400 font-normal">(What did you decide?)</span></label>
            <textarea
              className="input resize-none"
              rows={3}
              placeholder="We will use… because…"
              value={form.decision_text}
              onChange={(e) => setForm({ ...form, decision_text: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="label">Consequences <span className="text-gray-400 font-normal">(tradeoffs, risks)</span></label>
            <textarea
              className="input resize-none"
              rows={2}
              placeholder="Positive and negative consequences…"
              value={form.consequences}
              onChange={(e) => setForm({ ...form, consequences: e.target.value })}
            />
          </div>
          <div>
            <label className="label">Tags <span className="text-gray-400 font-normal">(comma-separated, or leave blank for AI suggestions)</span></label>
            <input
              className="input"
              placeholder="e.g. database, performance, security"
              value={form.tags}
              onChange={(e) => setForm({ ...form, tags: e.target.value })}
            />
          </div>
          <div className="flex gap-3 justify-end pt-2">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? 'Saving…' : 'Log Decision'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
