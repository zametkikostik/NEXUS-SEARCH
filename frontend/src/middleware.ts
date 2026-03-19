import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Rate limiting simple implementation
const rateLimit = new Map<string, { count: number; resetTime: number }>()

const RATE_LIMIT_WINDOW = 60 * 1000 // 1 minute
const RATE_LIMIT_MAX = 60 // requests per minute

export function middleware(request: NextRequest) {
  const ip = request.ip ?? '127.0.0.1'
  const now = Date.now()
  
  // Rate limiting
  const limit = rateLimit.get(ip)
  
  if (limit) {
    if (now > limit.resetTime) {
      // Reset window
      rateLimit.set(ip, { count: 1, resetTime: now + RATE_LIMIT_WINDOW })
    } else if (limit.count >= RATE_LIMIT_MAX) {
      return NextResponse.json(
        { error: 'Too many requests', retryAfter: Math.ceil((limit.resetTime - now) / 1000) },
        { status: 429 }
      )
    } else {
      limit.count += 1
      rateLimit.set(ip, limit)
    }
  } else {
    rateLimit.set(ip, { count: 1, resetTime: now + RATE_LIMIT_WINDOW })
  }
  
  // Security headers
  const response = NextResponse.next()
  response.headers.set('X-Content-Type-Options', 'nosniff')
  response.headers.set('X-Frame-Options', 'DENY')
  response.headers.set('X-XSS-Protection', '1; mode=block')
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
  
  return response
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}
