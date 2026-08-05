import { Card } from '@/components/ui/Card'

export function HistoryPage() {
  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-6">
      <h1 className="text-xl font-semibold text-slate-900">History</h1>

      <Card title="Previous analyses">
        <p className="text-sm text-slate-600">
          The sortable, filterable history table arrives in Phase 5.
        </p>
      </Card>
    </div>
  )
}
