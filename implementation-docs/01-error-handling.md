# Error Handling Implementation

## What is Error Handling?
Error handling is how your application responds when something goes wrong (like a missing file, network failure, or invalid input). Good error handling prevents crashes and gives users helpful messages.

## Before
- Errors were scattered across files with inconsistent messages
- Generic errors like "500 Internal Server Error" didn't explain the problem
- No centralized way to handle different error types
- Hard to track and debug issues

## After
- **Centralized error system** in `backend/app/core/errors.py`
- **Custom exceptions** for specific problems:
  - `BotNotFoundError` - When a bot doesn't exist
  - `BotAccessDeniedError` - When user can't access a bot
  - `DocumentProcessingError` - When file upload fails
  - `VectorStoreError` - When database operations fail
  - `AIServiceError` - When Groq API fails
  - `WebScraperError` - When website scraping fails
  - `AuthenticationError` - When login fails
  - `RateLimitError` - When too many requests are made

## Benefits
✅ **Consistent error format** - All errors return the same JSON structure  
✅ **Better debugging** - Errors are logged with context (path, method, details)  
✅ **User-friendly messages** - Clear explanations instead of technical jargon  
✅ **Proper HTTP codes** - 404 for not found, 403 for access denied, etc.  

## Example Error Response
```json
{
  "error": {
    "code": 404,
    "message": "Bot with ID 'abc-123' not found",
    "type": "BotNotFoundError"
  }
}
```

**Files Changed:**
- Created: `backend/app/core/errors.py`
- Updated: `backend/app/main.py`
- Updated: `backend/app/services/chat.py`
