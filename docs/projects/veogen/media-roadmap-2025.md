# VeoGen Media Roadmap – Q4 2025 Kickoff

## Objective
Track implementation of Flow ingest, Scene Describer, real-time prompt coaching, sound design upgrades, and compliance automation so Triple Initiatives milestones stay on schedule.

### Solo Dev Quick Checklist
- [ ] Work top-to-bottom: Phase A first, then B, C, etc.
- [ ] Keep a simple Kanban (To Do / Doing / Done) referencing these IDs.
- [ ] Update sprint column with actual week numbers you can commit to.
- [ ] If a row feels overkill, collapse it into your own issue tracker but keep status noted here.

## Phase A – Foundation (In Progress)
| ID | Work Item | Owner | Target Sprint | Dependencies | Notes |
| --- | --- | --- | --- | --- | --- |
| A1 | Build Flow webhook ingest service (`backend/flow/ingest.py`) and persist project metadata | Platform (Mira) | Sprint 2025.46 | Flow API preview access | Use feature flag `flow.enabled` |
| A2 | Mirror Flow ingredient assets to storage vault with SynthID metadata checks | Platform (Luis) | Sprint 2025.46 | A1 | Coordinate with SRE for storage quotas |
| A3 | Implement Scene Describer client + metadata pipeline | Platform (Noor) | Sprint 2025.46 | Gemini Vision entitlement | Store captions in `metadata/captions/` |
| A4 | Surface Scene Describer output in asset viewer + Flow timeline | Frontend (Jules) | Sprint 2025.47 | A3 | Include manual override UX |

## Phase B – UI Expansion (Pending)
| ID | Work Item | Owner | Target Sprint | Dependencies | Notes |
| --- | --- | --- | --- | --- | --- |
| B1 | Deliver Flow Studio tab (timeline, ingredient sidebar, approval checklist) | Frontend (Jules) | Sprint 2025.48 | A1, UX spec | Integrate feature flag |
| B2 | Launch Prompt Coach widget powered by Gemini Live | Frontend (Rhea) | Sprint 2025.49 | Realtime client, privacy doc | Provide accessibility toggles |
| B3 | Release Sound Design tab with AudioFX integration | Frontend (Ilan) | Sprint 2025.49 | AudioFX entitlement, UX spec | Fallback messaging for closed beta |

## Phase C – Compliance (Pending)
| ID | Work Item | Owner | Target Sprint | Dependencies | Notes |
| --- | --- | --- | --- | --- | --- |
| C1 | Configure SynthID analytics dashboard + BigQuery export | SRE (Anika) | Sprint 2025.47 | Vertex access | Share metrics with Release Flash |
| C2 | Build nightly watermark audit job (`compliance/synthid_audit.py`) | Platform (Luis) | Sprint 2025.48 | C1 | Alert Release Eng on failures |
| C3 | Create Compliance Center UI in Release dashboard | Frontend (Rhea) | Sprint 2025.48 | C1 | CSV export for legal review |

## Phase D – Experiments (Optional Pilot)
| ID | Work Item | Owner | Target Sprint | Dependencies | Notes |
| --- | --- | --- | --- | --- | --- |
| D1 | Pilot Gemini Live voice QA sessions with creative leads | Media AI (Sana) | Sprint 2025.50 | B2 | Capture feedback in Asana |
| D2 | Validate AudioFX loops in DAW MCP integration | Media AI (Theo) | Sprint 2025.50 | B3 | Ensure stems align with DAW tempo sync |

## Phase E – Workspace Automations (Backlog)
| ID | Work Item | Owner | Target Sprint | Dependencies | Notes |
| --- | --- | --- | --- | --- | --- |
| E1 | Create Docs “Brief to Flow” agent via Gemini Agent Builder | Productivity (Kai) | TBD | Flow GA | Requires Workspace admin approval |
| E2 | Ship Slides add-on for Imagen render sync | Productivity (Kai) | TBD | E1 | Display SynthID badge next to media |

## Tracking & Reporting
- Update status weekly in Release Flash standups.
- Mirror ticket IDs in Jira project `VEOMEDIA`.
- Use Grafana dashboard “Media Integrations” for telemetry (Flow ingest latency, Scene Describer throughput, SynthID audit results).

## Review Cadence
- Phase Gate reviews occur end of each sprint.
- Full roadmap review aligned with Triple Initiatives checkpoint or Flow GA announcement.*** End Patch

