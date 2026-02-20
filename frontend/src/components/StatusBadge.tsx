import clsx from 'clsx'
import type { DecisionStatus } from '../types'

const STATUS_CONFIG: Record<DecisionStatus, { label: string; classes: string }> = {
  proposed: { label: 'Proposed', classes: 'bg-yellow-100 text-yellow-800' },
  accepted: { label: 'Accepted', classes: 'bg-green-100 text-green-800' },
  deprecated: { label: 'Deprecated', classes: 'bg-gray-100 text-gray-600' },
  superseded: { label: 'Superseded', classes: 'bg-red-100 text-red-700' },
}

export default function StatusBadge({ status }: { status: DecisionStatus }) {
  const config = STATUS_CONFIG[status]
  return (
    <span className={clsx('inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium', config.classes)}>
      {config.label}
    </span>
  )
}
