import { Card } from '@/components/ui/Card'

export function PredictPage() {
  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">New analysis</h1>
        <p className="text-sm text-slate-600">
          Upload an oral lesion image and record the patient context.
        </p>
      </div>

      <Card title="Upload">
        <p className="text-sm text-slate-600">
          The image dropzone and the patient metadata form arrive in Phase 3.
        </p>
      </Card>
    </div>
  )
}
