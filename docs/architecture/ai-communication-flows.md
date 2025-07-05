# AI Communication Flows

This document illustrates the communication flows between VeoGen and Google's AI services (Veo Video API and Gemini API).

## Overview

VeoGen integrates with two main Google AI services:
- **Google Veo API** - For video generation
- **Google Gemini API** - For text enhancement and AI assistance

## Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant G as Google APIs
    
    U->>F: Enter API Keys
    F->>B: Save API Keys
    B->>B: Encrypt & Store Keys
    B->>G: Test API Connection
    G-->>B: Connection Status
    B-->>F: Validation Result
    F-->>U: Success/Error Message
```

## Video Generation Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant G as Gemini API
    participant V as Veo API
    participant DB as Database
    
    U->>F: Submit Video Prompt
    F->>B: POST /api/v1/video/generate
    B->>B: Validate API Keys
    B->>G: Enhance prompt with Gemini
    G-->>B: Enhanced prompt
    B->>V: Submit to Veo API
    V-->>B: Generation job ID
    B->>DB: Store job status
    
    loop Polling
        B->>V: Check generation status
        V-->>B: Processing/Complete/Failed
        B->>DB: Update status
    end
    
    alt Success
        V-->>B: Video URL & metadata
        B->>DB: Store video info
        B-->>F: Video ready notification
        F-->>U: Display video
    else Failure
        V-->>B: Error details
        B->>DB: Log error
        B-->>F: Error notification
        F-->>U: Show error message
    end
```

## Book Maker Flow

```mermaid
flowchart TD
    A[Create Book Project] --> B[Define Book Structure]
    B --> C[Set Title & Genre]
    C --> D[Configure Chapter Count]
    D --> E[Set Chapter Duration]
    
    E --> F[Chapter Planning]
    F --> G[AI-Generated Chapter Outline]
    G --> H[User Review & Edit]
    
    H --> I[Chapter Generation Queue]
    I --> J{Chapter Ready?}
    J -->|Yes| K[Generate Chapter Video]
    J -->|No| L[Wait for Dependencies]
    
    K --> M[Gemini: Enhance Chapter Content]
    M --> N[Veo: Generate Chapter Video]
    N --> O{Generation Success?}
    O -->|Yes| P[Save Chapter Video]
    O -->|No| Q[Error Handling & Retry]
    
    P --> R[Update Book Progress]
    R --> S{All Chapters Complete?}
    S -->|No| I
    S -->|Yes| T[Final Book Assembly]
    T --> U[Generate Book Trailer]
    U --> V[Book Complete]
```

## Movie Maker Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant G as Gemini API
    participant V as Veo API
    participant DB as Database
    
    U->>F: Create Movie Project
    F->>B: POST /api/v1/movies/create
    B->>DB: Save movie metadata
    B-->>F: Movie ID & Structure
    
    U->>F: Define Movie Structure
    F->>B: POST /api/v1/movies/{id}/scenes
    B->>G: Generate scene breakdown
    G-->>B: Structured scene plan
    B->>DB: Save scene structure
    
    U->>F: Generate Scene Video
    F->>B: POST /api/v1/movies/{id}/scenes/{scene}/generate
    B->>G: Enhance scene prompt
    G-->>B: Enhanced video prompt
    B->>V: Generate video scene
    V-->>B: Video generation job
    B->>DB: Update scene status
    
    loop Scene Processing
        B->>V: Check generation status
        V-->>B: Processing/Complete/Failed
        B->>DB: Update progress
    end
    
    B-->>F: Scene video ready
    F-->>U: Display scene video
    
    Note over U,DB: Repeat for all scenes
    Note over U,DB: Final movie assembly
```

## AI Enhancement Pipeline

```mermaid
flowchart TD
    A[User Input] --> B[Input Validation]
    B --> C[Content Analysis]
    C --> D[Gemini Enhancement]
    
    D --> E[Prompt Optimization]
    E --> F[Visual Element Enhancement]
    F --> G[Cinematic Detail Addition]
    G --> H[Style Consistency Check]
    
    H --> I[Enhanced Prompt Ready]
    I --> J[Submit to Veo API]
    J --> K[Video Generation]
    
    K --> L{Generation Quality}
    L -->|High Quality| M[Accept Video]
    L -->|Needs Improvement| N[Request Refinement]
    
    N --> O[Gemini: Analyze Issues]
    O --> P[Generate Improved Prompt]
    P --> J
```

## Error Handling & Recovery

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing: Start Generation
    Processing --> Success: Generation Complete
    Processing --> APIError: API Failure
    Processing --> Timeout: Generation Timeout
    
    APIError --> Retry: Automatic Retry
    Timeout --> Retry: Automatic Retry
    Retry --> Processing: Retry Generation
    Retry --> MaxRetries: Too Many Attempts
    
    MaxRetries --> UserNotification: Notify User
    UserNotification --> Idle: User Action
    
    Success --> Idle: Ready for Next
```

## API Rate Limiting

```mermaid
sequenceDiagram
    participant U as User
    participant B as Backend
    participant G as Google APIs
    participant Q as Queue Manager
    
    U->>B: Request Video Generation
    B->>B: Check Rate Limits
    alt Rate Limit Exceeded
        B->>Q: Add to Queue
        Q-->>B: Queue Position
        B-->>U: Queued Notification
    else Within Limits
        B->>G: Submit Request
        G-->>B: Processing
    end
    
    loop Queue Processing
        Q->>B: Process Next in Queue
        B->>G: Submit Request
        G-->>B: Result
        B-->>U: Update Status
    end
```

## Settings & Configuration

```mermaid
flowchart TD
    A[User Settings] --> B[API Configuration]
    B --> C[Google API Key]
    B --> D[Gemini API Key]
    B --> E[Google Cloud Project]
    
    A --> F[Generation Settings]
    F --> G[Default Duration]
    F --> H[Default Style]
    F --> I[Quality Preferences]
    
    A --> J[User Preferences]
    J --> K[Theme]
    J --> L[Notifications]
    J --> M[Auto-save]
    
    B --> N[Test API Connection]
    N --> O{Connection Valid?}
    O -->|Yes| P[Save Settings]
    O -->|No| Q[Show Error]
```

## Monitoring & Analytics

```mermaid
flowchart TD
    A[API Calls] --> B[Request Tracking]
    B --> C[Success Rate Monitoring]
    B --> D[Response Time Tracking]
    B --> E[Error Rate Analysis]
    
    C --> F[Performance Dashboard]
    D --> F
    E --> F
    
    F --> G[Alert System]
    G --> H[High Error Rate Alert]
    G --> I[Slow Response Alert]
    G --> J[API Limit Warning]
    
    H --> K[Admin Notification]
    I --> K
    J --> K
```

## Security Considerations

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant DB as Database
    participant G as Google APIs
    
    U->>F: Enter API Keys
    F->>B: Encrypt in Transit (HTTPS)
    B->>B: Hash & Encrypt Keys
    B->>DB: Store Encrypted Keys
    B->>G: Use Keys for API Calls
    
    Note over B: Keys never logged
    Note over B: Automatic key rotation
    Note over B: Access audit logging
```

---

## Next Steps

- [API Configuration Guide](../api/configuration.md)
- [Troubleshooting Guide](../troubleshooting/api-issues.md)
- [Performance Optimization](../performance/optimization.md) 