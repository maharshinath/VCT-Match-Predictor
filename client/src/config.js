/** Shared API / static origin. Empty = same host (Render production). */
export const API_ORIGIN = (import.meta.env.VITE_API_ORIGIN ?? 'http://127.0.0.1:5001').replace(
  /\/$/,
  ''
)

export const API_BASE = `${API_ORIGIN}/api`

export const DEFAULT_LOGO = `${API_ORIGIN}/static/logos/default-logo.svg`

export function logoUrl(path) {
  if (!path) return DEFAULT_LOGO
  if (/^https?:\/\//i.test(path)) return path
  return path.startsWith('/') ? `${API_ORIGIN}${path}` : `${API_ORIGIN}/${path}`
}
