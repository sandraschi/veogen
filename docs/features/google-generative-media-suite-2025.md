# Google Generative Media Suite 2025 Playbook

## Why This Matters
- Consolidates every Google facility VeoGen relies on for video, image, and music generation.
- Aligns with the **Great Doc Bash** target: clear guidance for engineers, producers, and release managers.
- Captures the newest Google releases (Veo 3.1, Imagen 4, Lyria 2, Flow) and how they plug into our `gemini-cli` workflows.

## Models at a Glance (2025-11)
| Model / Facility | Primary Output | 2025 Highlights | Access Path | Notes |
| --- | --- | --- | --- | --- |
| **Veo 3.1** | Cinematic video + native audio | Reference-image guidance (up to 3), first/last frame control, story timeline metadata | Gemini API via `gemini-cli` or Vertex AI | Paid preview; export up to ~60s, 4K pipeline in Flow [[1]] |
| **Gemini 3 Pro Image** (Nano Banana Pro) | High-fidelity images (2K/4K) | Enhanced typography, multilingual text rendering, studio-quality editing (lighting, camera angles, color grading), blend up to 14 images | Gemini API, Workspace (Slides/Vids), Adobe Firefly/Photoshop | Supports text rendering, background removal, 2K/4K outputs [[2]] |
| **Lyria 2 / Lyria RealTime** | Full-mix music + vocals | Real-time instrument control, choir-quality vocals, stem exports | Gemini API media endpoints, YouTube Music AI Sandbox | Latency targets <1.5s in RealTime mode [[3]] |
| **Flow** | Orchestrated film projects | Manages cast, locations, styles; stitches Veo + Imagen shots | Gemini Pro / Ultra subscribers (US roll-out) | Provides timeline + asset library for VeoGen ingest [[2]] |
| **Gemini 3.0 Pro (Media Ops)** | Text, control metadata, tool routing | Enhanced context, live collaboration, multi-modal reasoning | `gemini-cli`, Vertex AI | Used for storyboards, prompt QA, compliance reviews |
| **SynthID v2** | Secure provenance | Invisible + metadata watermarking for video, image, audio | Enabled by default on Vertex AI generations | Required for Release Flash readiness |

## Veo 3.1 Deep Dive
### Capability Snapshot
- **Prompt controls**: multi-sentence narratives, camera directives, motion verbs.
- **Visual continuity**: upload still frames or renders to lock characters/styles across scenes.
- **Audio**: automatic ambience, dialogue scaffolding, and timing data for post-mix.
- **Shot duration**: 5‒60 seconds; looping support for <10-second clips.

### Access & Tooling
1. Obtain Gemini API key with Veo entitlement (Vertex AI project or Gemini API Pro tier).  
2. In PowerShell:
   ```powershell
   cd D:\Dev\repos\veogen\gemini-cli
   uv run python -m gemini_cli.media video `
     -m veo-3.1 `
     -p "Rain-soaked neon alley, tracking shot, cyberpunk noir, include foley-ready footsteps" `
     --duration 45 `
     --frames-start .\refs\alley_start.png `
     --frames-end .\refs\alley_end.png
   ```
   > Verify `gemini_cli.media` subcommand path when the official CLI repo publishes—current nightly builds expose `media video`.
3. Store job metadata in `outputs/veo/` with SynthID hash for provenance.

### Integration Hooks
- **Story graph**: persist Veo job IDs in `backend/orchestration/story_graph.py`.
- **QA**: automate motion/lighting checks via `mcp-genmedia` services (connects to Veo preview frames).
- **Release Flash**: enforce SynthID validation before publishing dailies.

## Gemini 3 Pro Image Deep Dive (Nano Banana Pro)
### Capability Snapshot
- **Typography**: Improved multilingual text rendering for titles, UI mock-ups, comics, infographics, and posters.
- **Image blending**: Blend up to 14 images while maintaining visual consistency across multiple subjects.
- **Studio-quality editing**: Camera angle adjustments, lighting transformations, and color grading controls.
- **Resolutions**: 2K and 4K outputs across various aspect ratios (1:1, 4:5, 16:9, custom).
- **Context enrichment**: Powered by Google Search's knowledge base for more accurate, context-rich visuals.

### Access & Tooling
```powershell
cd D:\Dev\repos\veogen\gemini-cli
uv run python -m gemini_cli.media image `
  -m gemini-3.0-pro-image `
  -p "Ultra-wide desert rally poster with crisp sponsor typography, dusk lighting" `
  --aspect 16:9 `
  --safety "standard"
```
- Use Gemini 3 Pro Image outputs as Veo reference frames or marketing stills.
- Enable SynthID metadata propagation during asset ingest (`backend/assets/provenance.py`).

### Quality & Compliance
- Check for typography accuracy with `tools/qa/imagetext_validator.py`.
- Maintain safe-prompt library in `docs-private/imagen-safety-guidelines.md` (create if missing).

## Lyria 2 & Lyria RealTime
### Capability Snapshot
- **Vocal quality**: multi-voice choirs, emotion tags (e.g., `vox:gritty`, `vox:ethereal`).
- **RealTime mode**: stream prompts to adjust tempo, instrumentation mid-session (WebSocket API).
- **Stem delivery**: optional splits for vocals, drums, bass, FX.
- **Formats**: WAV 48 kHz (default), MP3 preview, MIDI sketch (beta).

### Access & Tooling
- Standard generation:
  ```powershell
  uv run python -m gemini_cli.media music `
    -m lyria-2 `
    -p "Ethereal synthwave suite with cinematic rises, 100 BPM, key of D minor" `
    --duration 120 `
    --stems vocals,drums,bass
  ```
- RealTime sessions: use `mcp-genmedia/clients/lyria_realtime.py` to maintain latency budgets and push updates from the UI transport controls.
- Route stems to our DAW integration (`docs/integrations/reaper-daw-mcp-integration.md`).

### Operational Notes
- Cache arrangement metadata (tempo, key, structure) for adaptive scoring.
- Embed SynthID audio watermarks before export to downstream editors.
- Monitor usage quotas; Lyria RealTime currently limited to 30 concurrent sessions per project.

## Flow Companion Platform
- **Purpose**: timeline workspace that merges Veo shots, Imagen concept art, Gemini scripts, and Lyria cues.
- **Key workflows for VeoGen**:
  - Import Flow shot lists into `frontend/src/features/storyboard`.
  - Sync Flow “ingredients” (characters, props, locations) with Veo reference frame storage.
  - Use Flow’s scene metadata to pre-fill `gemini-cli` prompt templates.
- **Limitations**: US-only beta, requires Gemini Pro or Ultra; export currently capped at 4K 30fps.

## Supporting Stack & Nice-to-Have Extras
- **Gemini Live & Sidekick**: real-time prompt debugging, on-the-fly storyboard edits.
- **Scene Describer API**: auto-caption Veo preview frames for accessibility tagging.
- **AudioFX (SoundStorm lineage)**: procedural sound effects model slated for GA—track via `mcp-genmedia` issue board.
- **Gemini Workspace Add-ons**: Slides + Docs integrations for marketing collateral.

## Integration Roadmap
| Phase | Sprint Goals | Deliverables | Owners |
| --- | --- | --- | --- |
| **Phase 0 – Readiness** | Verify entitlements, update credentials, enable SynthID logging | API key rotation doc, `config/gemini_media.json` | Platform |
| **Phase 1 – Core Pipelines** | Wire Veo, Imagen, Lyria via `gemini-cli`; implement storage adapters | `backend/orchestration/media_router.py`, asset vault updates | Media AI |
| **Phase 2 – Flow Sync** | Build Flow import/export, storyboard UI upgrades | Flow webhook consumer, storyboard UX refresh | Frontend |
| **Phase 3 – RealTime & Monitoring** | Add Lyria RealTime UI, integrate `monitoring/logging-architecture.md` hooks | Live mixing panel, Grafana dashboards | Audio + SRE |
| **Phase 4 – Compliance & Release** | Automate SynthID + policy checks, bundle release assets | Release Flash checklist updates, QA scripts | Release Eng |

## Testing, Observability, Compliance
- **Testing**: extend `tests/test_gemini_media.py` with regression prompts for each model; include golden hashes for frame/audio checks.
- **Observability**: pipe job status to Loki (`monitoring/loki-integration-guide.md`) and create Grafana panels per model type.
- **Compliance**: follow Google content policy—log prompt + output summary (hashed) with retention per `docs-private/TRIPLE_INITIATIVES_GUIDE.md`.
- **Fail-safes**: on API degradation, auto-fallback to cached outputs; notify via `systems/alerts/media_generation.yaml`.

## References
1. Google Developers Blog – *Introducing Veo 3.1 and new creative capabilities in the Gemini API* (2025).  
2. Google Blog – *Generative media models at Google I/O 2025* (Flow, Imagen 4, Veo updates).  
3. Google Blog – *Advances in generative music with Lyria and Music AI Sandbox* (2025).  
4. Official Gemini API Docs – *Media generation endpoints* (Vertex AI, Gemini API).  
5. Google Responsible AI Center – *SynthID watermarking for media safety* (2025 update).

---
*Maintainer*: Media Platform Team  
*Last reviewed*: 2025-11-12  
*Next audit*: with Release Flash milestone or when Google ships Veo 3.2 (whichever comes first)

