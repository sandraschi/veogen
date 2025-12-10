# Google Emerging Media Services 2025 Integration Plan

## Purpose
- Extend our Great Doc Bash coverage with actionable guidance on the newest Google creative facilities beyond Veo 3.1, Imagen 4, and Lyria 2.
- Prepare VeoGen UI and backend teams for Flow workspace sync, Gemini Live coaching, Scene Describer accessibility, AudioFX sound design, SynthID analytics, and Gemini Agent Builder automations.
- Deliver roadmap-level clarity for GitHub Dash and Release Flash milestones by mapping features, dependencies, and compliance requirements.

## Services Snapshot (2025-11)
| Service | Category | Highlights | Access Tier | Status for VeoGen |
| --- | --- | --- | --- | --- |
| **Flow** | Filmmaking workspace | Timeline orchestration, ingredient metadata (cast/locations), Veo shot management | Gemini Pro / Ultra (US preview) [[1]] | Targeted integration |
| **Gemini Live / Realtime API** | Conversational co-pilot | Low-latency voice + text interactions, prompt critique, live command execution | Gemini API (preview) [[2]] | Evaluate for prompt coach |
| **Scene Describer API** | Vision analysis | Generates structured captions, safety tags, accessibility text from frames | Gemini Vision API [[3]] | Immediate adoption |
| **AudioFX (SoundStorm lineage)** | Sound effects | Text-to-SFX, ambience layers, loopable assets | Experimental (AI Test Kitchen / Vertex AI preview) [[4]] | Pilot for sound design |
| **SynthID Analytics Dashboard** | Compliance | Centralized watermark telemetry, alerting for missing watermarks | Vertex AI console [[5]] | Required for Release Flash |
| **Gemini Agent Builder / Workspace Add-ons** | Automation | Workflow bots inside Docs, Slides, Chat, Drive with media shortcuts | Google Workspace Enterprise [[6]] | Optional (post-MVP) |

---

## Flow Integration Blueprint
### Capabilities
- Central “recipe” for scenes: characters, locations, props, styles, shot durations.
- Direct launch of Veo renders with trackable job IDs and thumbnail previews.
- Collaborative annotation for directors, producers, and editors.

### Backend Plan
1. **Webhook Listener**: Add `backend/flow/ingest.py` to process Flow project updates → store in `media_projects` table.
2. **Asset Sync**: Copy Flow “ingredient” assets (images, notes) to `storage://flow/{project}/{scene}`; ensure SynthID metadata preserved.
3. **Job Orchestration**: Map Flow shot entries to Veo queue via existing `media_router`, caching Flow’s desired start/end frames.

### UI Enhancements
- **New Tab**: `Flow Studio` under the navigation rail.
- **Modules**:
  - Scene timeline (drag-and-drop ordering, Flow status indicator).
  - Ingredient sidebar (characters, locations, props) with quick actions to open Imagen/Veo prompts.
  - Shot approval checklist (SynthID verified, audio mix attached, QC notes).
- **Collaboration**: Display Flow collaborator list + comment threads in a right side panel.

### Dependencies & Risks
- Flow currently US-only; implement feature flag `flow.enabled`.
- Export limit: 4K 30 fps; warn users when project goal exceeds current cap.
- Ensure Flow API tokens stored with least-privilege Vault role.

---

## Gemini Live / Realtime Prompt Coach
### Capabilities
- Conversational agent that listens to user voice or typed instructions, returns live coaching.
- Can call Gemini functions for prompt rewriting, storyboard critique, or compliance checks.
- Latency targets <400 ms for voice round-trips.

### Backend Plan
1. Extend `mcp-genmedia` with `realtime_client.py` handling WebRTC/WebSocket connection tokens and audio streaming.
2. Implement `prompt_review` tool hooking into existing prompt linting rules.
3. Log sessions to `monitoring/prompt_coach.jsonl` with anonymized transcripts and compliance tagging.

### UI Enhancements
- **New Pane**: “Prompt Coach” accessible from Veo, Imagen, Lyria workspaces (floating widget).
- Live waveform + transcript panel, real-time prompt rewrites, quick actions (“tighten camera directions”, “add safety tags”).
- Accessibility: closed captions toggle, audio device selection.

### Considerations
- Requires user opt-in for session recording.
- Tie into `docs-private/prompt-safety-checklist.md` to document policy adherence.

---

## Scene Describer API Rollout
### Capabilities
- Provides detailed captions, shot summaries, safety categories, and suggested alt-text.
- Supports batch mode for entire shot lists.

### Backend Plan
1. Add `vision/scene_describer.py` with async batch requests and retries.
2. Store outputs in `metadata/captions/{asset_id}.json`.
3. Feed alt-text into DAM and marketing toolchain.

### UI Enhancements
- **Upgrade Existing**: In the asset viewer, add Description tab showing auto captions + manual edit toggle.
- Provide one-click export to accessibility packages (HTML + JSON).
- Integrate with Flow Studio timeline: auto-populate caption column.

### Compliance
- Run content policy heuristics, flag flagged content for manual review.
- Log API latency and error rates in Grafana (Loki pipeline already in place).

---

## AudioFX Pilot
### Capabilities
- Generates sound effects, ambiences, Foley loops from text prompts.
- Supports parameter control (loop length, intensity, emotion).

### Backend Plan
1. Register `audiofx` provider under `media_router`.
2. Cache loops in `outputs/audiofx/{project}` with SynthID metadata.
3. Integrate with DAW MCP module for direct drag-and-drop into Reaper or Ableton sessions.

### UI Enhancements
- **New Tab**: “Sound Design” (coexists with Lyria tab).
- Prompt form with categories (ambience, Foley, UI FX), loop toggle, BPM sync for Lyria integration.
- Preview mini DAW strip with waveform view and loop markers.

### Risks & Mitigation
- Preview program availability limited; build graceful fallback message.
- Monitor licensing terms before public release.

---

## SynthID Analytics & Compliance
### Capabilities
- Cross-service dashboard showing watermark application rates, detection confidence, anomalies.
- API hooks for real-time alerts when a generation lacks SynthID.

### Backend Plan
1. Configure Vertex AI SynthID project dashboards; export metrics to BigQuery.
2. Build nightly job `compliance/synthid_audit.py` verifying all assets flagged “publish-ready”.
3. Integrate alerting via `systems/alerts/media_generation.yaml` to page Release Flash on watermark failures.

### UI Enhancements
- **New Section**: “Compliance Center” inside Release dashboard.
- Show per-asset watermark status with links to remediation steps.
- Provide CSV export for legal review.

---

## Gemini Agent Builder & Workspace Add-ons
### Capabilities
- Create no-code agents that interact with Gemini models + Google Workspace.
- Can trigger VeoGen APIs from Slides/Docs/Chat via custom actions.

### Integration Concept
- Build “VeoGen Brief Assistant” agent to transform Docs story briefs into Flow projects and prompt templates.
- Create Slides add-on that pulls the latest Imagen renders into presentations with SynthID verification badges.

### UI/Workflow Impact
- Add “Workspace Sync” settings panel to connect user Workspace accounts.
- Provide documentation on creating personal agents mapped to VeoGen API scopes.

### Security
- Enforce OAuth with domain-wide delegation approvals.
- Log all agent-triggered actions for auditing.

---

## Implementation Roadmap
| Phase | Focus | Primary Deliverables | Owners |
| --- | --- | --- | --- |
| **Phase A – Foundation** | Flow ingest + Scene Describer | Flow webhook service, metadata models, asset captions | Platform |
| **Phase B – UI Expansion** | Flow Studio, Prompt Coach widget, Sound Design tab | Frontend components, design system updates | Frontend |
| **Phase C – Compliance** | SynthID analytics integration | Vertex dashboard config, Compliance Center UI, alerting | SRE + Release |
| **Phase D – Experiments** | Gemini Live, AudioFX pilots | MCP clients, RealTime QA, DAW integration tests | Media AI |
| **Phase E – Workspace Automations** | Agent Builder + Workspace sync | OAuth flows, Docs/Slides add-ons, docs updates | Productivity |

---

## Testing & Monitoring
- Extend `tests/test_flow_ingest.py`, `tests/test_scene_describer.py`, and add `tests/test_prompt_coach_realtime.py`.
- Add Grafana dashboards: Flow webhook latency, Scene Describer throughput, RealTime session quality, SynthID missing watermark alerts.
- Ensure fallback messaging for geo-restricted services (Flow, AudioFX).

---

## References
1. Google Blog – *Generative media models at Google I/O 2025* (Flow overview).  
2. Google Blog – *Gemini Live: real-time multimodal agents* (2025 I/O).  
3. Google AI – *Gemini API Vision: Scene Describer update* (2025).  
4. Google Research – *Advances in generative audio with SoundStorm & AudioFX* (2025).  
5. Google Responsible AI Center – *SynthID v2 analytics for compliance teams* (2025 update).  
6. Google Workspace Blog – *Gemini Agent Builder & Workspace add-ons for media teams* (2025).

---
*Maintainer*: Media Platform Team  
*Last reviewed*: 2025-11-13  
*Next review*: Align with Flow GA or Gemini Live general availability (whichever is earlier)

