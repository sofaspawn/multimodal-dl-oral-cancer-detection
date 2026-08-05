import { useParams } from 'react-router-dom'

import { Card } from '@/components/ui/Card'
import { DisclaimerBanner } from '@/components/layout/DisclaimerBanner'

export function ResultPage() {
  const { id } = useParams<{ id: string }>()

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-6">
      <h1 className="text-xl font-semibold text-slate-900">
        Prediction {id}
      </h1>

      <DisclaimerBanner className="rounded-md border" />

      <Card title="Result">
        <p className="text-sm text-slate-600">
          The confidence gauge, Grad-CAM heatmap viewer and report download
          arrive in Phase 4.
        </p>
      </Card>
    </div>
  )
}
