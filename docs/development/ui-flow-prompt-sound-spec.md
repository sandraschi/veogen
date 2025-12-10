# UI Spec: Flow Studio, Prompt Coach, Sound Design Tabs

## Author & Context
- Author: GPT-5 Codex (Media Platform)
- Date: 2025-11-13
- Linked roadmap: `docs/projects/veogen/media-roadmap-2025.md`
- Goal: Provide actionable UX direction so design can deliver mockups before development sprints 2025.48–2025.49.

### Solo Dev Quick Checklist
- Treat each section (Flow Studio, Prompt Coach, Sound Design) as a mini feature; build one at a time.
- Use rough sketches or simple wireframes before coding—no need for formal mockups.
- Copy the component lists into your issue tracker as acceptance criteria.
- If a feature is feature-flagged off for now, still follow the layout so it’s easy to toggle later.

---

## Flow Studio Tab
### Primary Personas
- **Creative Director**: arranges scenes, reviews assets, assigns notes.
- **Producer**: monitors status, ensures compliance checks pass.

### Information Architecture
1. **Scene Timeline (center)**: horizontal timeline with cards per scene/shot.
2. **Ingredient Sidebar (left)**: collapsible panels for Characters, Locations, Objects with quick actions.
3. **Detail Drawer (right)**: opens on card click, showing Flow metadata, Veo job ID, approvals, SynthID status.

### Key Components
- Timeline card:
  - Thumbnail (Flow poster frame) 120×68.
  - Title, duration, status pill (`Draft`, `Queued`, `Rendered`, `Needs Fix`).
  - Inline icons for SynthID, Audio mix, Captions.
- Ingredient chips: show asset name + type icon; hover reveals actions (Open in Imagen, Attach to scene).
- Approval checklist (bottom of detail drawer):
  - `Prompt finalized`, `SynthID confirmed`, `Scene described`, `Audio mix attached`.
  - Each item linkable to source artifact.

### Interactions
- Drag to reorder scenes; drop triggers re-sync call (show toast “Scene order updated”).
- Clicking “Launch Render” triggers Veo job modal (prefilled from Flow metadata).
- Feature flag gating: show banner “Flow sync limited to US preview accounts”.

### Accessibility & Responsiveness
- Keyboard navigation for timeline cards (arrow keys + Enter).
- Ensure color contrast meets WCAG AA for status pills.
- Mobile view: switch to stacked list with collapsible detail sections.

---

## Prompt Coach Widget (Gemini Live)
### Placement
- Floating widget anchored bottom-right within Veo, Imagen, Lyria, AudioFX tabs.
- Collapsible to 56×56 FAB; expanded width 420 px, height 560 px.

### Layout
1. **Header**: title “Prompt Coach”, indicator (Live/Idle), settings icon.
2. **Transcript pane**: conversational bubbles with timestamps.
3. **Input bar**: text area + microphone toggle + “Send” button.
4. **Quick Actions** row: chips like “Tighten camera directions”, “Add safety tags”, “Simplify lighting”.
5. **Insights panel** (collapsible): bullet feedback on prompt clarity, constraint alignment.

### States
- Idle, Listening (animated waveform), Processing (spinner), Response (text/html suggestions).
- Error state with retry button and link to privacy notice.

### Accessibility
- Live captions for spoken output; ARIA alerts for state changes.
- Session consent modal on first launch with explicit checkbox.

### Telemetry
- Log interactions (action invoked, duration) to `monitoring/prompt_coach.jsonl`.
- Provide “Report Issue” link for user feedback.

---

## Sound Design Tab (AudioFX)
### Layout
1. **Prompt Form** (left column):
   - Text prompt field (multi-line).
  - Category dropdown (Ambience, Foley, UI FX, Creature, Sci-Fi).
  - Duration selector (5s-60s) + Loop toggle.
  - Intensity slider (Low/Med/High).
  - Tempo sync input (BPM) for Lyria alignment.
2. **Preview Panel** (right column):
   - Waveform visualization with loop markers.
   - Play/Pause, Download, Add to Project buttons.
   - Metadata summary (SynthID hash, sample rate, stems).

### Secondary Elements
- Recent generations list (bottom) with quick re-run.
- Beta access banner when feature flag disabled.
- Link to DAW integration guide for drag-and-drop instructions.

### Interactions
- Generate button triggers loader + status toasts.
- When loop enabled, waveform displays fade-in/out markers; allow user to adjust.
- “Send to DAW” opens modal listing connected MCP DAWs.

### Accessibility
- Keyboard shortcuts (Space = play/pause, L = loop toggle).
- Provide textual waveform summary for screen readers (duration, peaks, dynamics).

### Error Handling
- If AudioFX unavailable, show card with CTA “Request Access” linking to support ticket template.
- Ensure fallback sound library surfaces curated library entries.

---

## Cross-cutting Requirements
- Internationalization: copy strings into locale files; default en-US.
- Analytics: track tab open, generation requests, error states in existing telemetry schema.
- Feature Flags: `flow.enabled`, `prompt_coach.enabled`, `audiofx.enabled`; display environment-specific banners.
- Security/Privacy: ensure microphone input respects consent; show SynthID status on every downloadable asset.

---

## Deliverables for Design Team
- High-fidelity mockups (desktop + tablet + mobile) for Flow Studio timeline, Prompt Coach expanded/collapsed, Sound Design tab default/error states.
- Interaction specs (micro-interactions, transitions) referencing this document.
- Accessibility checklist per component.

Once mockups approved, handoff to engineering for sprint 2025.48 planning.*** End Patch

