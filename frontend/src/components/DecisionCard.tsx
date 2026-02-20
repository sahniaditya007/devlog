import { Link } from 'react-router-dom'
import { ArrowRight, Tag, User } from 'lucide-react'
import StatusBadge from './StatusBadge'
import type { Decision } from '../types'

export default function DecisionCard({ decision }: { decision: Decision }) {
  return (
    <div className="card p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <StatusBadge status={decision.status} />
            {decision.tags.slice(0, 3).map((tag) => (
              <span key={tag} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-brand-50 text-brand-700">
                <Tag size={10} />
                {tag}
              </span>
            ))}
          </div>
          <h3 className="font-semibold text-gray-900 truncate">{decision.title}</h3>
          {decision.ai_summary ? (
            <p className="text-sm text-gray-500 mt-1 line-clamp-2">{decision.ai_summary}</p>
          ) : (
            <p className="text-sm text-gray-500 mt-1 line-clamp-2">{decision.context}</p>
          )}
          <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
            <span className="flex items-center gap-1">
              <User size={11} />
              {decision.author_name}
            </span>
            <span>{new Date(decision.created_at).toLocaleDateString()}</span>
            {decision.links.length > 0 && (
              <span>{decision.links.length} link{decision.links.length !== 1 ? 's' : ''}</span>
            )}
          </div>
        </div>
        <Link
          to={`/decisions/${decision.id}`}
          className="flex-shrink-0 p-2 rounded-lg text-gray-400 hover:text-brand-600 hover:bg-brand-50 transition-colors"
        >
          <ArrowRight size={16} />
        </Link>
      </div>
    </div>
  )
}
