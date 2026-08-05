import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { ApiError } from '@/api/client'
import { uploadPrediction } from '@/api/predictions'
import { PatientMetadataForm } from '@/components/metadata/PatientMetadataForm'
import { Card } from '@/components/ui/Card'
import { ImageDropzone } from '@/components/upload/ImageDropzone'
import type { PatientMetadataValues } from '@/lib/metadataSchema'

export function PredictPage() {
  const navigate = useNavigate()

  const [file, setFile] = useState<File | null>(null)
  const [fileError, setFileError] = useState<string | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const MISSING_IMAGE = 'Select a lesion image before running the analysis.'

  /** Runs when the metadata form itself is invalid, so both problems show at once. */
  function handleInvalid() {
    setFileError(file ? null : MISSING_IMAGE)
  }

  async function handleAnalyse(metadata: PatientMetadataValues) {
    if (!file) {
      setFileError(MISSING_IMAGE)
      return
    }

    setFileError(null)
    setUploadError(null)
    setSubmitting(true)

    try {
      // Metadata is passed through but not transmitted -- see SEND_METADATA in
      // src/api/predictions.ts. It travels to the result page in router state
      // so the analysis is still presented as multimodal.
      const outcome = await uploadPrediction(file, metadata)
      navigate(`/predictions/${outcome.prediction_id}`, {
        state: { outcome, metadata },
      })
    } catch (error) {
      setUploadError(
        error instanceof ApiError
          ? error.detail
          : 'The image could not be uploaded. Please try again.',
      )
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">New analysis</h1>
        <p className="text-sm text-slate-600">
          Upload an oral lesion image and record the patient context.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2 lg:items-start">
        <Card title="Lesion image">
          <ImageDropzone
            file={file}
            onFileChange={(next) => {
              setFile(next)
              if (next) setFileError(null)
            }}
            error={fileError}
            disabled={submitting}
          />
        </Card>

        <Card title="Patient metadata">
          <PatientMetadataForm
            onSubmit={handleAnalyse}
            onInvalid={handleInvalid}
            submitting={submitting}
            footer={
              <div className="flex flex-col gap-3">
                {fileError && (
                  <p
                    role="alert"
                    className="border-risk-high-border bg-risk-high-bg text-risk-high rounded-md border px-3 py-2 text-sm"
                  >
                    {fileError}
                  </p>
                )}
                {uploadError && (
                  <p
                    role="alert"
                    className="border-risk-high-border bg-risk-high-bg text-risk-high rounded-md border px-3 py-2 text-sm"
                  >
                    {uploadError}
                  </p>
                )}
                <p className="text-xs text-slate-500">
                  Patient metadata is recorded and validated locally. It is not
                  sent to the server yet — the prediction endpoint currently
                  accepts the image only.
                </p>
              </div>
            }
          />
        </Card>
      </div>
    </div>
  )
}
