# Rate Limiting Implementation

## What is Rate Limiting?
Rate limiting controls how many requests a user can make to your API in a given time period. It prevents abuse, protects your server from overload, and ensures fair usage for all users.

## Before
- No protection against API abuse
- Anyone could spam unlimited requests
- Risk of server overload and high costs (AI API calls are expensive)
- No defense against malicious bots or attackers

## After
- **Two-tier rate limiting system:**
  
  **General API Rate Limits:**
  - 60 requests per minute per IP
  - 1,000 requests per hour per IP
  
  **Chat Endpoint Rate Limits (stricter):**
  - 20 chat requests per minute per IP
  - 200 chat requests per hour per IP

## How It Works
1. **Tracks each IP address** separately
2. **Counts requests** in rolling time windows (per minute and per hour)
3. **Blocks excessive requests** with HTTP 429 error
4. **Returns "Retry-After" header** telling users when they can try again
5. **Auto-cleanup** removes old IP data to save memory

## Benefits
✅ **Prevents API abuse** - Stops automated scripts from overwhelming your server  
✅ **Controls costs** - Limits expensive AI API calls  
✅ **Fair usage** - All users get equal access  
✅ **Server protection** - Prevents crashes from too many requests  
✅ **Headers included** - Users can see their remaining quota

## Example Headers
```
X-RateLimit-Limit-Minute: 60
X-RateLimit-Remaining-Minute: 45
X-RateLimit-Limit-Hour: 1000
X-RateLimit-Remaining-Hour: 892
```

## When Rate Limited
```json
{
  "error": {
    "code": 429,
    "message": "Too many requests. Please slow down.",
    "retry_after_seconds": 42
  }
}
```

**Files Changed:**
- Created: `backend/app/core/rate_limiter.py`
- Updated: `backend/app/main.py`
