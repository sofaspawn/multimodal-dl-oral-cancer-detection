import { Link } from 'react-router-dom'

import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { useAuth } from '@/hooks/useAuth'

export function DashboardPage() {
  const { user } = useAuth()

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">Dashboard</h1>
          <p className="text-sm text-slate-600">
            Signed in as {user?.email}
          </p>
        </div>
        <Link to="/predict">
          <Button>New analysis</Button>
        </Link>
      </div>

      <Card title="Summary">
        <p className="text-sm text-slate-600">
          Summary cards and recent predictions arrive in Phase 5, once the
          history table and formatting helpers exist.
        </p>
      </Card>
    </div>
  )
}
