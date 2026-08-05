/**
 * Prediction endpoints.
 *
 * Only POST /predict exists on the backend today, and it returns just
 * {filename, status, message} -- see backend/app/routers/prediction.py. The
 * other functions are written against the contract in BACKEND_API.md and work
 * against fixtures until those routes ship.
 */

import { getJson, postForm, resolveUrl, USE_MOCKS } from './client'
import * as mocks from './mocks'
import type {
  PatientMetadata,
  PredictionHistoryEntry,
  PredictionOutcome,
  PredictionUploadResponse,
} from './types'

/**
 * Whether patient metadata is appended to the upload request.
 *
 * Currently false by decision: the form is built and validated, but POST
 * /predict has no metadata contract yet, so we send the image alone. The
 * append logic below is written and ready -- flipping this constant to true is
 * the only change needed once the backend accepts the fields.
 */
const SEND_METADATA: boolean = false

export async function uploadPrediction(
  file: File,
  metadata?: PatientMetadata,
): Promise<PredictionOutcome> {
  if (USE_MOCKS) return mocks.uploadPrediction(file, metadata)

  const form = new FormData()
  form.append('file', file)

  if (SEND_METADATA && metadata) {
    for (const [key, value] of Object.entries(metadata)) {
      if (value !== undefined && value !== null && value !== '') {
        form.append(key, String(value))
      }
    }
  }

  const response = await postForm<PredictionUploadResponse>('/predict', form)

  // The live endpoint stores the image and returns no prediction -- there is no
  // model behind it yet. Synthesise an outcome flagged as pending rather than
  // inventing a class and a confidence the backend never produced.
  return {
    prediction_id: -1,
    prediction: 'Pending',
    confidence: 0,
    heatmap_url: null,
    pdf_url: null,
    created_at: new Date().toISOString(),
    filename: response.filename,
    image_url: URL.createObjectURL(file),
    is_pending_inference: true,
  }
}

export function listPredictions(): Promise<PredictionHistoryEntry[]> {
  if (USE_MOCKS) return mocks.listPredictions()
  return getJson<PredictionHistoryEntry[]>('/predictions')
}

export function getPrediction(id: number): Promise<PredictionOutcome> {
  if (USE_MOCKS) return mocks.getPrediction(id)
  return getJson<PredictionOutcome>(`/predictions/${id}`)
}

/** Absolute URL of the generated PDF report, for a download link. */
export function reportUrl(predictionId: number): string {
  return resolveUrl(`/reports/${predictionId}`)
}
