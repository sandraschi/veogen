---
title: Email Verification Route Issue
type: note
permalink: issues-email-verification-route-issue
---

# Email Verification Issue - Missing Route

## Problem Found
The `resend-verification` endpoint returns 404 because it's not appearing in the OpenAPI spec. This indicates the route is not being registered properly.

## Cause
Python syntax error in enhanced_auth.py - missing except block was preventing the function from loading properly.

## Current Status
- Registration emails work (saved to dev_emails/)
- Password reset emails work  
- Resend verification has route registration issue
- Need to test with Sandra's real email: sandraschipal@hotmail.com

## Next Steps
1. Fix the missing route registration
2. Test with real email address
3. Verify email flows work end-to-end