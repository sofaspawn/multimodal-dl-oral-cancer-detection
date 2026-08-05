import { useLocation, useParams } from 'react-router-dom'

import type { PredictionOutcome } from '@/api/types'
import { DisclaimerBanner } from '@/components/layout/DisclaimerBanner'
import { MetadataSummary } from '@/components/result/MetadataSummary'
import { Card } from '@/components/ui/Card'
import type { PatientMetadataValues } from '@/lib/metadataSchema'

interface ResultLocationState {
  outcome?: PredictionOutcome
  metadata?: PatientMetadataValues
}

export function ResultPage() {
  const { id } = useParams<{ id: string }>()
  const location = useLocation()
  const state = (location.state as ResultLocationState | null) ?? {}

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-6">
      <h1 className="text-xl font-semibold text-slate-900">
        {state.outcome ? 'Analysis result' : `Prediction ${id}`}
      </h1>

      <DisclaimerBanner className="rounded-md border" />

      <div className="grid gap-6 lg:grid-cols-2 lg:items-start">
        <Card title="Result">
          {state.outcome?.is_pending_inference ? (
            <p className="text-sm text-slate-600">
              The image was uploaded and stored as{' '}
              <code className="rounded bg-slate-100 px-1 py-0.5 font-mono text-xs">
                {state.outcome.filename}
              </code>
              . No prediction is available: the backend has no model behind{' '}
              <code className="rounded bg-slate-100 px-1 py-0.5 font-mono text-xs">
                /predict
              </code>{' '}
              yet.
            </p>
          ) : (
            <p className="text-sm text-slate-600">
              The confidence gauge, Grad-CAM heatmap viewer and report download
              arrive in Phase 4.
            </p>
          )}

          {state.outcome?.image_url && (
            <img
              src={state.outcome.image_url}
              alt="Analysed oral lesion"
              className="border-surface-border mt-4 max-h-64 rounded-md border object-contain"
            />
          )}
        </Card>

        <Card title="Patient context">
          {state.metadata ? (
            <MetadataSummary metadata={state.metadata} />
          ) : (
            <p className="text-sm text-slate-600">
              No patient metadata was recorded with this analysis. Metadata is
              captured at upload time and is not stored on the server yet.
            </p>
          )}
        </Card>
      </div>
    </div>
  )
}
