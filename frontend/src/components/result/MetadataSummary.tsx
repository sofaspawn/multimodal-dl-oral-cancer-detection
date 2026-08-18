import {
  METADATA_FIELD_LABELS,
  formatMetadataValue,
  type PatientMetadataValues,
} from '@/lib/metadataSchema'

/** Renders submitted patient metadata back to the clinician for review. */
export function MetadataSummary({
  metadata,
}: {
  metadata: PatientMetadataValues
}) {
  const keys = Object.keys(METADATA_FIELD_LABELS) as Array<
    keyof PatientMetadataValues
  >

  return (
    <dl className="grid gap-x-6 gap-y-3 sm:grid-cols-2">
      {keys.map((key) => {
        const value = metadata[key]
        // Optional follow-ups are omitted rather than shown as blank rows.
        if (value === undefined) return null

        return (
          <div key={key} className="flex flex-col">
            <dt className="text-xs text-slate-500">
              {METADATA_FIELD_LABELS[key]}
            </dt>
            <dd className="text-sm text-slate-900">
              {formatMetadataValue(key, value)}
            </dd>
          </div>
        )
      })}
    </dl>
  )
}
