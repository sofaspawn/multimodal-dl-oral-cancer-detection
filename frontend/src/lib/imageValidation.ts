/**
 * Client-side image validation.
 *
 * Mirrors the server rules in backend/app/services/prediction_service.py and
 * backend/app/core/config.py. This is a courtesy check for fast feedback, not
 * a security boundary -- the backend rejects bad files regardless, and its
 * error text is what the user sees if these two ever disagree.
 */

/** Matches settings.ALLOWED_EXTENSIONS. */
export const ALLOWED_EXTENSIONS = [
  '.jpg',
  '.jpeg',
  '.png',
  '.bmp',
  '.tiff',
  '.webp',
] as const

/** Matches settings.MAX_FILE_SIZE_MB. */
export const MAX_FILE_SIZE_MB = 10

const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

/** The accept attribute for the file input, derived from the same list. */
export const ACCEPT_ATTRIBUTE = ALLOWED_EXTENSIONS.join(',')

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

/** Returns an error message, or null when the file is acceptable. */
export function validateImageFile(file: File): string | null {
  const dot = file.name.lastIndexOf('.')
  const extension = dot === -1 ? '' : file.name.slice(dot).toLowerCase()

  if (!ALLOWED_EXTENSIONS.includes(extension as (typeof ALLOWED_EXTENSIONS)[number])) {
    return `Unsupported file type${extension ? ` '${extension}'` : ''}. Allowed types: ${ALLOWED_EXTENSIONS.join(', ')}.`
  }

  if (file.size > MAX_FILE_SIZE_BYTES) {
    return `Image is ${formatFileSize(file.size)}. The maximum size is ${MAX_FILE_SIZE_MB} MB.`
  }

  if (file.size === 0) {
    return 'That file is empty.'
  }

  return null
}
