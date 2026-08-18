import { z } from 'zod'

import type { PatientMetadata } from '@/api/types'

/**
 * Patient metadata form schema -- the second modality.
 *
 * Field names match the PatientMetadata contract in src/api/types.ts exactly,
 * and the assertion at the bottom of this file fails the build if they ever
 * drift apart. The values are validated but not transmitted; see SEND_METADATA
 * in src/api/predictions.ts.
 */

export const SEX_OPTIONS = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'other', label: 'Other' },
] as const

export const TOBACCO_TYPE_OPTIONS = [
  { value: 'smoked', label: 'Smoked (cigarette, bidi, cigar)' },
  { value: 'smokeless', label: 'Smokeless (chewing, snuff, gutkha)' },
  { value: 'both', label: 'Both' },
] as const

export const LESION_SITE_OPTIONS = [
  { value: 'buccal_mucosa', label: 'Buccal mucosa' },
  { value: 'tongue', label: 'Tongue' },
  { value: 'gingiva', label: 'Gingiva' },
  { value: 'palate', label: 'Palate' },
  { value: 'floor_of_mouth', label: 'Floor of mouth' },
  { value: 'lip', label: 'Lip' },
] as const

const YES_NO_REQUIRED = 'Select yes or no'

export const patientMetadataSchema = z
  .object({
    age: z
      .number({ error: 'Enter the patient age' })
      .int('Age must be a whole number')
      .min(1, 'Age must be at least 1')
      .max(120, 'Age must be 120 or below'),
    sex: z.enum(['male', 'female', 'other'], {
      error: 'Select the patient sex',
    }),

    tobacco_use: z.boolean({ error: YES_NO_REQUIRED }),
    tobacco_type: z.enum(['smoked', 'smokeless', 'both']).optional(),
    tobacco_years: z
      .number()
      .int('Enter a whole number of years')
      .min(0, 'Years cannot be negative')
      .max(100, 'Enter 100 years or fewer')
      .optional(),

    betel_quid_use: z.boolean({ error: YES_NO_REQUIRED }),
    alcohol_use: z.boolean({ error: YES_NO_REQUIRED }),

    lesion_site: z.enum(
      [
        'buccal_mucosa',
        'tongue',
        'gingiva',
        'palate',
        'floor_of_mouth',
        'lip',
      ],
      { error: 'Select the lesion site' },
    ),
    lesion_duration_weeks: z
      .number({ error: 'Enter how long the lesion has been present' })
      .int('Enter a whole number of weeks')
      .min(0, 'Duration cannot be negative')
      .max(520, 'Enter 520 weeks (10 years) or fewer'),

    pain: z.boolean({ error: YES_NO_REQUIRED }),
    bleeding: z.boolean({ error: YES_NO_REQUIRED }),
    prior_lesion_history: z.boolean({ error: YES_NO_REQUIRED }),
  })
  // The tobacco follow-ups are only meaningful, and only required, when the
  // patient uses tobacco.
  .superRefine((values, ctx) => {
    if (!values.tobacco_use) return

    if (!values.tobacco_type) {
      ctx.addIssue({
        code: 'custom',
        path: ['tobacco_type'],
        message: 'Select the type of tobacco used',
      })
    }

    if (values.tobacco_years === undefined) {
      ctx.addIssue({
        code: 'custom',
        path: ['tobacco_years'],
        message: 'Enter the number of years of use',
      })
    }
  })

export type PatientMetadataValues = z.infer<typeof patientMetadataSchema>

/**
 * Compile-time guarantee that the form produces exactly what the API expects.
 * If a field is renamed here but not in PatientMetadata (or vice versa), this
 * resolves to `false` and `tsc` fails.
 */
type Expect<T extends true> = T
export type MetadataMatchesApiContract = Expect<
  PatientMetadataValues extends PatientMetadata ? true : false
>

/** Human-readable labels, for rendering a submitted record back to the user. */
export const METADATA_FIELD_LABELS: Record<keyof PatientMetadataValues, string> =
  {
    age: 'Age',
    sex: 'Sex',
    tobacco_use: 'Tobacco use',
    tobacco_type: 'Tobacco type',
    tobacco_years: 'Years of tobacco use',
    betel_quid_use: 'Betel quid / areca nut',
    alcohol_use: 'Alcohol use',
    lesion_site: 'Lesion site',
    lesion_duration_weeks: 'Lesion duration',
    pain: 'Pain',
    bleeding: 'Bleeding',
    prior_lesion_history: 'Prior oral lesion',
  }

function labelFrom(
  options: ReadonlyArray<{ value: string; label: string }>,
  value: string,
): string {
  return options.find((option) => option.value === value)?.label ?? value
}

/** Format one metadata value for display. */
export function formatMetadataValue(
  key: keyof PatientMetadataValues,
  value: PatientMetadataValues[keyof PatientMetadataValues],
): string {
  if (value === undefined) return '—'
  if (typeof value === 'boolean') return value ? 'Yes' : 'No'

  switch (key) {
    case 'age':
      return `${value} years`
    case 'lesion_duration_weeks':
      return `${value} ${value === 1 ? 'week' : 'weeks'}`
    case 'tobacco_years':
      return `${value} ${value === 1 ? 'year' : 'years'}`
    case 'sex':
      return labelFrom(SEX_OPTIONS, String(value))
    case 'tobacco_type':
      return labelFrom(TOBACCO_TYPE_OPTIONS, String(value))
    case 'lesion_site':
      return labelFrom(LESION_SITE_OPTIONS, String(value))
    default:
      return String(value)
  }
}
