import { USE_MOCKS } from '@/api/client'
import { reportUrl } from '@/api/predictions'
import { Button } from '@/components/ui/Button'

interface ReportDownloadProps {
  predictionId: number
  pdfUrl: string | null
}

export function ReportDownload({ predictionId, pdfUrl }: ReportDownloadProps) {
  if (!pdfUrl) {
    return (
      <Button
        variant="secondary"
        disabled
        title="No PDF report has been generated for this prediction yet."
        className="w-full"
      >
        Report unavailable
      </Button>
    )
  }

  return (
    <div className="flex flex-col gap-2">
      {/* An anchor, not a button: this is a navigation to a file, so
          middle-click and "save link as" should behave normally. */}
      <a
        href={reportUrl(predictionId)}
        download
        className="bg-brand-600 hover:bg-brand-700 inline-flex h-10 w-full items-center justify-center gap-2 rounded-md px-4 text-sm font-medium text-white transition-colors"
      >
        <svg
          viewBox="0 0 20 20"
          fill="currentColor"
          className="h-4 w-4"
          aria-hidden="true"
        >
          <path d="M10 2a.75.75 0 0 1 .75.75v7.19l2.22-2.22a.75.75 0 1 1 1.06 1.06l-3.5 3.5a.75.75 0 0 1-1.06 0l-3.5-3.5a.75.75 0 1 1 1.06-1.06l2.22 2.22V2.75A.75.75 0 0 1 10 2zM3.5 14.5a.75.75 0 0 1 .75.75v.5a.75.75 0 0 0 .75.75h10a.75.75 0 0 0 .75-.75v-.5a.75.75 0 0 1 1.5 0v.5a2.25 2.25 0 0 1-2.25 2.25H5a2.25 2.25 0 0 1-2.25-2.25v-.5a.75.75 0 0 1 .75-.75z" />
        </svg>
        Download PDF report
      </a>
      {USE_MOCKS && (
        <p className="text-xs text-slate-500">
          The link follows the planned contract. Report generation is not
          implemented on the backend yet, so it will not resolve.
        </p>
      )}
    </div>
  )
}
