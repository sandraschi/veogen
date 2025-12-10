# Google Media Services Access Checklist

## Overview
Use this checklist before enabling new Google facilities inside VeoGen. Capture project IDs, entitlement status, approval dates, and owners so audits remain effortless.

### Solo Dev Quick Checklist
- Make a copy of this file and fill blanks as you request access; it’s just your personal log.
- “Request submitted by” = you. “Owner” = you.
- If a service isn’t available yet, mark it “n/a” so you remember it’s pending.
- Keep all credential references (like `vault://...`) pointing to wherever you securely store secrets (even if that’s just 1Password/Git-ignored file).

## Flow Workspace (Veo/Imagen orchestration)
- [ ] Google Cloud project ID with Flow beta access:
  - Project: `________`
  - Request submitted by: `________`
  - Approval date: `________`
- [ ] Gemini API Pro or Ultra subscription confirmed.
- [ ] Regional availability (US-only) acknowledged; feature flag `flow.enabled` documented.
- [ ] Service account `veogen-flow-sync` created with least-privilege scopes.
- [ ] Vault entry updated with Flow API credentials reference (`vault://google/flow`).

## AudioFX (SoundStorm lineage)
- [ ] AI Test Kitchen / Vertex AI preview enrollment submitted.
- [ ] Usage limits documented (loops per day, concurrent jobs).
- [ ] Contact at Google Media Partnerships assigned.
- [ ] Compliance review for generated FX licensing stored in `legal/audiofx`.
- [ ] Fallback messaging defined for users without access.

## Gemini Live / Realtime API
- [ ] Realtime quota approved (sessions per minute).
- [ ] WebRTC token endpoint configured (`config/realtime.json`).
- [ ] Privacy notice updated and legal sign-off recorded.
- [ ] Logging retention policy confirmed (<30 days for raw transcripts).

## Scene Describer (Gemini Vision)
- [ ] Vision API enabled on project `________`.
- [ ] Billing alerts configured for batch caption jobs.
- [ ] Content moderation escalation path documented.

## SynthID Analytics Dashboard
- [ ] Vertex AI SynthID dashboard activated.
- [ ] BigQuery export dataset created (`veogen_synthid.analytics`).
- [ ] Alert channel configured (PagerDuty / email).
- [ ] Compliance Center UI feature flag `synthid.dashboard` recorded.

## Gemini Agent Builder / Workspace Add-ons
- [ ] Workspace domain admin approval captured.
- [ ] OAuth consent screen updated with VeoGen scopes.
- [ ] Data processing agreement signed (if required).
- [ ] Agent audit log destination configured (BigQuery / Chronicle).

## Sign-off
- Media Platform Lead: `________` (date)
- Security & Compliance Lead: `________` (date)
- Release Flash Owner: `________` (date)

Maintain this checklist in sync with roadmap updates; update entries whenever Google changes preview terms or access tiers.*** End Patch

