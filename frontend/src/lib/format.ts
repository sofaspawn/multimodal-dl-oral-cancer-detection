/** Display formatting helpers shared by the result page and history table. */

import type { SeverityLevel } from '@/api/types'

/** 0.96 -> "96%" */
export function formatPercent(value: number): string {
  return `${Math.round(value * 100)}%`
}

export interface ConfidenceBand {
  label: 'Low' | 'Moderate' | 'High'
  description: string
}

/**
 * Plain-language reading of a confidence score.
 *
 * A bare "0.71" invites over-reading. The wording deliberately frames every
 * band as needing clinical review rather than as a verdict.
 */
export function confidenceBand(value: number): ConfidenceBand {
  if (value < 0.7) {
    return {
      label: 'Low',
      description:
        'The model is not confident in this result. Treat it as inconclusive.',
    }
  }

  if (value < 0.85) {
    return {
      label: 'Moderate',
      description:
        'The model leans towards this result but is not certain. Clinical correlation is required.',
    }
  }

  return {
    label: 'High',
    description:
      'The model is confident in this result. Clinical confirmation is still required.',
  }
}

export interface SeverityBand {
  label: string
  description: string
  color: string
}

/**
 * Severity categorization for cancer predictions.
 *
 * Severity is derived from the model's confidence score and indicates
 * the aggressiveness or progression of the suspected lesion.
 */
export function severityBand(severity: SeverityLevel | null): SeverityBand | null {
  if (!severity) return null

  switch (severity) {
    case 'mild':
      return {
        label: 'Mild',
        description: 'Early-stage lesion with less aggressive features.',
        color: 'text-amber-600',
      }
    case 'moderate':
      return {
        label: 'Moderate',
        description: 'Established lesion with intermediate characteristics.',
        color: 'text-orange-600',
      }
    case 'severe':
      return {
        label: 'Severe',
        description: 'Advanced or highly aggressive features detected.',
        color: 'text-red-600',
      }
    default:
      return null
  }
}

/** ISO timestamp -> "5 Aug 2026, 14:32" in the viewer's locale. */
export function formatDateTime(iso: string): string {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return iso

  return date.toLocaleString(undefined, {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
