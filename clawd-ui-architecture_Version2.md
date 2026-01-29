# Clawd4Dummies UI Architecture & Implementation Plan

## Executive Summary

This document outlines the UI design architecture for Clawd4Dummies, a security assessment tool targeting non-technical users. The design prioritizes clarity, accessibility, and actionable guidance while maintaining a distinctive visual identity.

---

## 1. Design Philosophy

### 1.1 Aesthetic Direction: "Security Control Room"

**Concept:** A modern security operations center aesthetic - dark theme with high-contrast severity indicators, inspired by mission control dashboards. Professional yet approachable for non-technical users.

**Core Principles:**

- **Clarity over complexity** - Non-technical users must immediately understand their security status
- **Action-oriented** - Every finding leads to clear remediation steps
- **Trust-building** - Transparent, local-only operation messaging throughout
- **Progressive disclosure** - Summary first, details on demand

### 1.2 Visual Identity

| Element | Specification |
|---------|---------------|
| Primary Background | `#0D1117` (deep space black) |
| Card Background | `#161B22` (elevated surface) |
| Text Primary | `#E6EDF3` (high contrast) |
| Text Secondary | `#7D8590` (muted) |
| Accent | `#58A6FF` (action blue) |
| Critical | `#F85149` (red alert) |
| High | `#DB6D28` (orange warning) |
| Medium | `#D29922` (yellow caution) |
| Low | `#3FB950` (green safe) |
| Info | `#8B949E` (neutral gray) |

**Typography:**

- **Display/Headers:** "JetBrains Mono" - technical credibility
- **Body:** "IBM Plex Sans" - readable, professional
- **Monospace (code/paths):** "Fira Code" - ligatures for clarity

---

## 2. UI Components Architecture

### 2.1 Application Shell

```
┌─────────────────────────────────────────────────────────────────┐
│  HEADER BAR                                                      │
│  ┌─────────────┬──────────────────────────┬──────────────────┐  │
│  │ Logo/Title  │     Status Indicator     │  Export Actions  │  │
│  └─────────────┴──────────────────────────┴──────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  MAIN CONTENT AREA                                               │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    RISK DASHBOARD                          │  │
��  │              (Hero Section - Always Visible)               │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    SCAN CONTROLS                           │  │
│  │           (Quick/Full Scan + Module Selection)             │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                  FINDINGS SECTION                          │  │
│  │        (Expandable Cards by Severity Category)             │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   SYSTEM INFO                              │  │
│  │              (Collapsible Footer Panel)                    │  │
│  └───────────────────────────────────────────────────────────┘  │
├───────────────���─────────────────────────────────────────────────┤
│  FOOTER: Privacy Notice + Version                                │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Breakdown

#### A. Risk Dashboard (Hero Section)

**UI Pattern:** Dashboard + Completeness Meter

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│     ┌─────────────────────────────────────────────────────┐     │
│     │                   RISK GAUGE                         │     │
│     │                                                      │     │
│     │            ╭──────────────────────╮                 │     │
│     │           ╱    CRITICAL RISK      ╲                │     │
│     │          │         9.2            │                │     │
│     │          │        ─────           │                │     │
│     │          │         10             │                │     │
│     │           ╲    Immediate Action   ╱                │     │
│     │            ╰──────────────────────╯                 │     │
│     │                                                      │     │
│     │   [█████████░] 92% Risk                             │     │
│     │                                                      │     │
│     └─────────────────────────────────────────────────────┘     │
│                                                                  │
│     ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐            │
│     │ CRIT: 2 │ │ HIGH: 3 │ │ MED: 1  │ │ LOW: 2  │            │
│     │   🔴    │ │   🟠    │ │   🟡    │ │   🟢    │            │
│     └─────────┘ └─────────┘ └─────────┘ └─────────┘            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**

- Animated radial gauge (0-10 scale)
- Color-coded based on risk level
- Severity count badges with click-to-filter
- Pulsing animation for CRITICAL status
- Plain English status message

#### B. Scan Controls Panel

**UI Pattern:** Module Tabs + Morphing Controls

```
┌─────────────────────────────────────────────────────────────────┐
│  SCAN OPTIONS                                                    │
│  ─────────────                                                   │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐                     │
│  │   ⚡ QUICK SCAN   │  │   🔍 FULL SCAN    │                     │
│  │   Port + Config  │  │   All Modules    │                     │
│  │   ~30 seconds    │  │   ~2 minutes     │                     │
│  └──────────────────┘  └──────────────────┘                     │
│                                                                  │
│  ▼ Advanced: Select Modules                                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ☑ Port Scanner      ☑ Credential Scanner   ☑ Config Analyzer││
│  │ ☑ Process Monitor   ☑ File Permissions     ☑ Network Analyzer│
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│           [ ▶ START SECURITY SCAN ]                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**

- Two primary scan modes with clear descriptions
- Expandable advanced section (Progressive Disclosure pattern)
- Module checkboxes with tooltips explaining each
- Large, prominent action button
- Disabled state during active scan

#### C. Progress Indicator (During Scan)

**UI Pattern:** Steps Left + Wizard

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│     🔍 SCANNING YOUR SYSTEM                                     │
│     ─────────────────────────                                   │
│                                                                  │
│     [████████████░░░░░░░░░░░░░░░░░░] 45%                        │
│                                                                  │
│     ✓ Port Scanner .............. Complete                      │
│     ✓ Credential Scanner ........ Complete                      │
│     ● Config Analyzer ........... In Progress                   │
│     ○ Process Monitor ........... Pending                       │
│     ○ File Permissions .......... Pending                       │
│     ○ Network Analyzer .......... Pending                       │
│                                                                  │
│     Current: Checking claude_desktop_config.json...             │
│                                                                  │
│     [ ⏹ CANCEL SCAN ]                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**

- Animated progress bar with percentage
- Step-by-step module completion status
- Real-time current operation display
- Cancel button with confirmation dialog
- Estimated time remaining (optional)

#### D. Findings Display

**UI Pattern:** Cards + Categorization + Progressive Disclosure

```
┌─────────────────────────────────────────────────────────────────┐
│  SECURITY FINDINGS                                    [Filter ▼]│
│  ═════════════════                                               │
│                                                                  │
│  🔴 CRITICAL ISSUES (2) - Fix IMMEDIATELY                       │
│  ───────────────────────────────────────                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ▼ Clawdbot Gateway Exposed to Network            CVSS: 9.5 ││
│  │   ─────────────────────────────────────────────────────────  ││
│  │   Your Clawdbot gateway (port 18789) is accessible from     ││
│  │   the internet. Anyone can connect to your computer!        ││
│  │                                                              ││
│  │   📍 Location: Port 18789 bound to 0.0.0.0                  ││
│  │                                                              ││
│  │   🔧 HOW TO FIX:                                            ││
│  │   ┌────────────────────────────────────────────────────────┐││
│  │   │ 1. Open your Clawdbot configuration file               │││
│  │   │ 2. Find the "bind" setting                             │││
│  │   │ 3. Change "0.0.0.0" to "127.0.0.1"                     │││
│  │   │ 4. Save and restart Clawdbot                           │││
│  │   │                                            [📋 Copy]   │││
│  │   └────────────────────────────────────────────────────────┘││
│  │                                                              ││
│  │   📚 Learn More: [Security Best Practices →]                ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ▶ Authentication Bypass Vulnerability            CVSS: 9.0 ││
│  │   Click to expand...                                        ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  🟠 HIGH ISSUES (3) - Fix within 24 hours                       │
│  ─────────────────────────────────────────                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ▶ API Keys Found in Plain Text                   CVSS: 8.5 ││
│  └─────────────────────────────────────────────────────────────┘│
│  ...                                                             │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**

- Grouped by severity with clear headers
- Expandable/collapsible cards (Accordion pattern)
- CVSS score badge on each finding
- Plain English descriptions (no jargon)
- Step-by-step remediation with copy button
- Reference links for additional learning
- Filter dropdown (All/Critical/High/Medium/Low)

#### E. Remediation Copy Box

**UI Pattern:** Copy Box + Inline Help

```
┌─────────────────────────────────────────────────────────────────┐
│  🔧 STEPS TO FIX:                                               │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                                                              ││
│  │  1. Open your Clawdbot configuration file:                  ││
│  │     📁 %APPDATA%\Claude\claude_desktop_config.json          ││
│  │                                                              ││
│  │  2. Find this line:                                         ││
│  │     │ "bind": "0.0.0.0"                                     ││
│  │                                                              ││
│  │  3. Change it to:                                           ││
│  │     │ "bind": "127.0.0.1"                                   ││
│  │                                                              ││
│  │  4. Save the file and restart Clawdbot                      ││
│  │                                                              ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │  [📋 Copy Steps]  [📂 Open Config Location]  [❓ Help]      ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

**Features:**

- Numbered steps with clear formatting
- File paths with "Open Location" quick action
- Code snippets with syntax highlighting
- Copy to clipboard with success toast notification
- Help link for each remediation step

#### F. Report Export Panel

**UI Pattern:** Settings + Morphing Controls

```
┌─────────────────────────────────────────────────────────────────┐
│  📊 EXPORT REPORT                                               │
│  ─────────────────                                              │
│                                                                  │
│  Choose Format:                                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐│
│  │ 📄 HTML     │ │ 📋 JSON     │ │ 📝 Markdown │ │ 🖨 Print   ││
│  │ Visual     │ │ Machine     │ │ Shareable   │ │ Paper     ││
│  │ Report     │ │ Readable    │ │ (GitHub)    │ │ Report    ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────────┘│
│                                                                  │
│  ☑ Include System Information                                   │
│  ☑ Include Remediation Steps                                    │
│  ☐ Include Technical Details (Advanced)                         │
│                                                                  │
│  Filename: clawd_security_report_2026-01-27                     │
│                                                                  │
│            [ 💾 DOWNLOAD REPORT ]                               │
│                                                                  │
└───────────────────────────────────────���─────────────────────────┘
```

**Features:**

- Format selection cards with descriptions
- Customization checkboxes
- Auto-generated filename with date
- Preview option before download
- Success confirmation with file location

#### G. System Information Panel

**UI Pattern:** Dashboard + FAQ

```
┌─────────────────────────────────────────────────────────────────┐
│  ▼ SYSTEM INFORMATION                                           │
│  ─────────────────────                                          │
│                                                                  │
│  ┌─────────────────────┬─────────────────────┬─────────────────┐│
│  │ 💻 Platform         │ 👤 User             │ 🔐 Privileges   ││
│  │ Windows 10          │ john_doe            │ Standard User   ││
│  └─────────────────────┴─────────────────────┴─────────────────┘│
│  ┌─────────────────────┬─────────────────────┬─────────────────┐│
│  │ 🐍 Python           │ 🌐 Local IPs        │ 📅 Scan Time    ││
│  │ 3.11.4              │ 192.168.1.100       │ 2026-01-27      ││
│  │                     │ 10.0.0.5            │ 14:32:15        ││
│  └─────────────────────┴─────────────────────┴─────────────────┘│
│                                                                  │
│  ⓘ This scan was performed locally. No data was sent externally.│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**

- Collapsible by default (Progressive Disclosure)
- Grid layout for quick scanning
- Privacy reassurance message
- Timestamp of scan completion

---

## 3. UI Patterns Applied

| Component | UI Patterns Used | Purpose |
|-----------|------------------|---------|
| Risk Dashboard | Dashboard, Completeness Meter | At-a-glance status |
| Scan Controls | Module Tabs, Morphing Controls | Flexible scan options |
| Progress | Steps Left, Wizard | Clear progress feedback |
| Findings | Cards, Accordion, Categorization | Organized vulnerability display |
| Remediation | Copy Box, Inline Help | Actionable fix instructions |
| Export | Settings, Modal | Report generation |
| System Info | Dashboard, FAQ | Contextual information |
| Filtering | Table Filter, Tagging | Finding management |
| Notifications | Notifications, Input Feedback | User feedback |

---

## 4. Interaction States

### 4.1 State Machine

```
┌─────────┐     ┌──────────┐     ┌───────────┐     ┌──────────┐
│  IDLE   │ ──▶ │ SCANNING │ ──▶ │ COMPLETE  │ ──▶ │ EXPORTED │
│         │     │          │     │           │     │          │
│ • Start │     │ • Cancel │     │ • Re-scan │     │ • New    │
│   Scan  │     │ • View   │     │ • Export  │     │   Scan   │
│         │     │   Status │     │ • Filter  │     │          │
└─────────┘     └──────────┘     └───────────┘     └──────────┘
      ▲                                │                  │
      └────────────────────────────────┴──────────────────┘
```

### 4.2 Visual States per Component

| Component | Default | Hover | Active | Disabled | Loading |
|-----------|---------|-------|--------|----------|---------|
| Scan Button | Blue fill | Lighten 10% | Scale 98% | Gray, 50% opacity | Spinner |
| Finding Card | Border left | Elevate shadow | Expanded | N/A | Skeleton |
| Copy Button | Icon only | Show tooltip | Success checkmark | N/A | N/A |
| Severity Badge | Solid color | Glow effect | N/A | Muted | N/A |

---

## 5. Responsive Design

### 5.1 Breakpoints

| Breakpoint | Width | Layout Adjustments |
|------------|-------|-------------------|
| Desktop | >1200px | Full 3-column dashboard |
| Tablet | 768-1200px | 2-column, stacked panels |
| Mobile | <768px | Single column, collapsible sections |

### 5.2 Mobile Considerations

- Findings cards full-width
- Bottom sheet for export options
- Swipe to expand/collapse sections
- Floating action button for scan start
- Touch-friendly tap targets (min 44px)

---

## 6. Accessibility Requirements

| Requirement | Implementation |
|-------------|----------------|
| Color Contrast | WCAG AA minimum (4.5:1 for text) |
| Keyboard Navigation | Full tab order, Enter/Space activation |
| Screen Readers | ARIA labels, role attributes, live regions |
| Motion | Respect prefers-reduced-motion |
| Focus Indicators | Visible focus rings on all interactive elements |

---

## 7. Animation Specifications

### 7.1 Key Animations

| Element | Animation | Duration | Easing |
|---------|-----------|----------|--------|
| Risk Gauge | Count up + color transition | 1.5s | ease-out |
| Progress Bar | Width expansion | 300ms | linear |
| Card Expand | Height + opacity | 250ms | ease-in-out |
| Severity Pulse | Scale + glow (CRITICAL only) | 2s loop | ease-in-out |
| Copy Success | Checkmark morph | 200ms | ease-out |
| Page Load | Staggered fade-in | 50ms delay each | ease-out |

### 7.2 Micro-interactions

- Button hover: subtle scale (1.02) + shadow increase
- Card hover: elevation increase (shadow depth)
- Toggle switches: smooth slide with color transition
- Toast notifications: slide in from top-right, auto-dismiss

---

## 8. Technology Stack (CONFIRMED)

### 8.1 Selected Stack: React + Electron

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Shell | Electron 28+ | Cross-platform desktop, native feel |
| Framework | React 18+ | Component-based, large ecosystem |
| Styling | Tailwind CSS + CSS Modules | Utility-first with scoped styles |
| Animation | Framer Motion | Declarative animations |
| Icons | Lucide React | Consistent, customizable |
| Charts | Recharts | Risk gauge, progress visuals |
| State | Zustand | Lightweight state management |
| Build | Vite | Fast development, optimized builds |
| IPC | Electron IPC | Python backend communication |
| Packaging | electron-builder | Distribution (Windows, macOS, Linux) |

### 8.2 Deployment Model: Standalone GUI App

- Separate executable launcher (Clawd4Dummies.exe / Clawd4Dummies.app)
- Independent of CLI installation
- Bundles Python runtime OR connects to system Python
- Users choose between GUI or CLI based on preference

---

## 9. File Structure

### 9.1 Electron + React GUI Application

```
clawd-for-dummies-gui/                 # Standalone GUI project
├── package.json                       # Node dependencies
├── electron/
│   ├── main.js                        # Electron main process
│   ├── preload.js                     # Context bridge
│   └── python-bridge.js               # IPC to Python backend
├── src/
│   ├── App.tsx                        # Root React component
│   ├── main.tsx                       # React entry point
│   ├── index.css                      # Global styles + Tailwind
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppShell.tsx           # Main application frame
│   │   │   ├── Header.tsx             # Top bar with actions
│   │   │   └── Footer.tsx             # Privacy notice + version
│   │   ├── dashboard/
│   │   │   ├── RiskDashboard.tsx      # Hero section with gauge
│   │   │   ├── RiskGauge.tsx          # Animated radial gauge
│   │   │   └── SeverityCounts.tsx     # Badge counts
���   │   ├── scan/
│   │   │   ├── ScanControls.tsx       # Quick/Full scan buttons
│   │   │   ├── ModuleSelector.tsx     # Checkbox module selection
│   │   │   └── ProgressIndicator.tsx  # Step-by-step progress
│   │   ├── findings/
│   │   │   ├── FindingsDisplay.tsx    # Main findings container
│   │   │   ├── FindingCard.tsx        # Expandable finding card
│   │   │   ├── RemediationBox.tsx     # Copy-to-clipboard steps
│   │   │   └── SeverityBadge.tsx      # Color-coded badge
│   │   ├── export/
│   │   │   └── ExportPanel.tsx        # Report format selection
│   │   ├── system/
│   │   │   └── SystemInfo.tsx         # Collapsible system details
│   │   └── common/
│   │       ├── Button.tsx
│   │       ├── Card.tsx
│   │       ├── ProgressBar.tsx
│   │       ├── Toast.tsx
│   │       └── Tooltip.tsx
│   ├── hooks/
│   │   ├── useScanner.ts              # Scanner state management
│   │   ├── useClipboard.ts            # Copy functionality
│   │   └── useExport.ts               # Report generation
│   ├── stores/
│   │   └── scanStore.ts               # Zustand store
│   ├── types/
│   │   ├── finding.ts                 # TypeScript interfaces
│   │   └── scan.ts
│   └── utils/
│       ├── theme.ts                   # Color/typography tokens
│       └── animations.ts              # Framer Motion variants
├── tailwind.config.js                 # Tailwind configuration
├── vite.config.ts                     # Vite build config
└── electron-builder.yml               # Packaging configuration
```

### 9.2 Python Backend Integration

```
clawd_for_dummies/
├── ...existing structure...
├── api/                               # New: API for GUI communication
│   ├── __init__.py
│   ├── server.py                      # Local HTTP/WebSocket server
│   └── handlers.py                    # Scan/export request handlers
```

---

## 10. Implementation Phases

### Phase 1: Core Components (Week 1-2)

- [ ] Application shell with theme
- [ ] Risk Dashboard with gauge
- [ ] Basic scan controls
- [ ] Progress indicator

### Phase 2: Findings Display (Week 2-3)

- [ ] Finding cards with severity styling
- [ ] Accordion expand/collapse
- [ ] Remediation copy box
- [ ] Category filtering

### Phase 3: Export & Polish (Week 3-4)

- [ ] Export panel implementation
- [ ] System info display
- [ ] Animations and micro-interactions
- [ ] Accessibility audit

### Phase 4: Integration & Testing (Week 4-5)

- [ ] Connect to scanner backend
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Cross-platform testing

---

## 11. Verification Plan

### 11.1 Testing the UI

**Visual Testing**

- Compare against design specifications
- Test all severity color states
- Verify responsive breakpoints

**Functional Testing**

- Scan initiation and cancellation
- Progress updates in real-time
- Finding card expand/collapse
- Copy to clipboard functionality
- Export all formats

**Integration Testing**

- Connect UI to scanner backend
- Verify data flow (findings → display)
- Test error states and edge cases

**Accessibility Testing**

- Screen reader navigation
- Keyboard-only operation
- Color contrast validation

### 11.2 User Acceptance Criteria

- [ ] Non-technical user can start a scan in <3 clicks
- [ ] Risk level is immediately apparent on page load
- [ ] Remediation steps are copy-paste ready
- [ ] Export generates valid files in all formats
- [ ] All critical findings display with urgency indicators

---

## 12. Critical Files to Modify

| File | Changes |
|------|---------|
| `clawd_for_dummies/interface/__init__.py` | Add GUI module exports |
| `clawd_for_dummies/__main__.py` | Add `--gui` flag to launch GUI |
| `clawd_for_dummies/scanner.py` | Add progress callback hooks |
| `clawd_for_dummies/report_generator.py` | Add GUI-compatible data format |
| `setup.py` | Add GUI dependencies |
| `requirements.txt` | Add GUI libraries |

---

## 13. Best Practices & Standards (MANDATORY)

This section defines non-negotiable engineering standards based on [Electron Performance Guidelines](https://www.electronjs.org/docs/latest/tutorial/performance) and [Vercel React Best Practices](https://vercel.com/blog/react-best-practices).

### 13.1 Electron Performance Standards

**Reference:** https://www.electronjs.org/docs/latest/tutorial/performance

#### A. Startup Optimization

| Rule | Implementation | Priority |
|------|----------------|----------|
| Lazy Module Loading | Load scanner modules only when scan starts, not at app launch | CRITICAL |
| Defer Heavy Dependencies | Load Recharts, Framer Motion after initial render | CRITICAL |
| Bundle Code | Use Vite to bundle into single file, reduce require() overhead | HIGH |
| Skip Default Menu | Call Menu.setApplicationMenu(null) before app ready | MEDIUM |

```typescript
// ❌ BAD: Eager loading
import { AnimatePresence } from 'framer-motion';
import { PieChart } from 'recharts';

// ✅ GOOD: Lazy loading
const AnimatePresence = lazy(() =>
  import('framer-motion').then(m => ({ default: m.AnimatePresence }))
);
const PieChart = lazy(() =>
  import('recharts').then(m => ({ default: m.PieChart }))
);
```

#### B. IPC Communication Rules

| Rule | Requirement |
|------|-------------|
| Never use synchronous IPC | All ipcRenderer.invoke() must be async |
| Avoid @electron/remote | Use contextBridge + preload script exclusively |
| Batch IPC calls | Group related data requests into single IPC call |
| Typed IPC channels | Define strict TypeScript types for all channels |

```typescript
// electron/preload.ts - REQUIRED PATTERN
import { contextBridge, ipcRenderer } from 'electron';

// Define typed API
interface ScannerAPI {
  startScan: (modules: string[]) => Promise<void>;
  onProgress: (callback: (progress: ScanProgress) => void) => void;
  cancelScan: () => Promise<void>;
}

contextBridge.exposeInMainWorld('scanner', {
  startScan: (modules) => ipcRenderer.invoke('scanner:start', modules),
  onProgress: (callback) => ipcRenderer.on('scanner:progress', (_, data) => callback(data)),
  cancelScan: () => ipcRenderer.invoke('scanner:cancel'),
} satisfies ScannerAPI);
```

#### C. Process Architecture

| Process | Responsibilities | Forbidden Operations |
|---------|------------------|---------------------|
| Main Process | Window management, IPC routing, Python bridge | Heavy computation, synchronous I/O |
| Renderer Process | UI rendering, user interaction | Direct file system access, Node APIs |
| Python Backend | Scanning, analysis, report generation | UI updates (must go through IPC) |

```typescript
// ❌ BAD: Blocking main process
const result = fs.readFileSync('/path/to/config');

// ✅ GOOD: Non-blocking with worker
const worker = new Worker('./scanner-worker.js');
worker.postMessage({ type: 'scan', modules });
```

#### D. Memory Management

| Rule | Implementation |
|------|----------------|
| Remove event listeners | Always call removeListener in cleanup |
| Clear timers | Clear all setInterval/setTimeout on unmount |
| Dispose large objects | Set to null after use, especially scan results |
| Profile heap regularly | Use Chrome DevTools Memory tab during development |

```typescript
// React component with proper cleanup
useEffect(() => {
  const unsubscribe = window.scanner.onProgress(handleProgress);

  return () => {
    unsubscribe(); // REQUIRED: Remove listener
  };
}, []);
```

### 13.2 React Performance Standards

**Reference:** Vercel React Best Practices

#### A. Eliminating Waterfalls (CRITICAL)

| Rule ID | Rule | Application |
|---------|------|-------------|
| async-parallel | Use Promise.all() for independent operations | Scan module initialization |
| async-defer-await | Move await into branches where needed | Conditional report generation |
| async-suspense-boundaries | Use Suspense for streaming | Finding cards loading |

```typescript
// ❌ BAD: Sequential waterfall
const portResult = await scanPorts();
const credResult = await scanCredentials();
const configResult = await analyzeConfig();

// ✅ GOOD: Parallel execution
const [portResult, credResult, configResult] = await Promise.all([
  scanPorts(),
  scanCredentials(),
  analyzeConfig(),
]);
```

#### B. Bundle Size Optimization (CRITICAL)

| Rule ID | Rule | Application |
|---------|------|-------------|
| bundle-barrel-imports | Import directly, avoid barrel files | Component imports |
| bundle-dynamic-imports | Use next/dynamic equivalent | Heavy components |
| bundle-defer-third-party | Load analytics after hydration | N/A (no analytics) |

```typescript
// ❌ BAD: Barrel import
import { Button, Card, Badge } from '@/components';

// ✅ GOOD: Direct imports
import { Button } from '@/components/common/Button';
import { Card } from '@/components/common/Card';
import { Badge } from '@/components/findings/SeverityBadge';
```

#### C. Re-render Optimization (MEDIUM)

| Rule ID | Rule | Application |
|---------|------|-------------|
| rerender-memo | Extract expensive work into memoized components | FindingCard list |
| rerender-derived-state | Subscribe to derived booleans, not raw values | Filter state |
| rerender-functional-setstate | Use functional setState for stable callbacks | Scan progress updates |
| rerender-lazy-state-init | Pass function to useState for expensive values | Initial findings parse |

```typescript
// ❌ BAD: Inline object causing re-renders
<FindingCard style={{ borderColor: getSeverityColor(finding.severity) }} />

// ✅ GOOD: Memoized style
const cardStyle = useMemo(() => ({
  borderColor: getSeverityColor(finding.severity)
}), [finding.severity]);
<FindingCard style={cardStyle} />
```

#### D. Component Patterns

```typescript
// REQUIRED: Memoize list items
const FindingCard = memo(function FindingCard({ finding }: { finding: Finding }) {
  // Component implementation
});

// REQUIRED: Stable callbacks
const handleExpand = useCallback((id: string) => {
  setExpandedIds(prev => prev.includes(id)
    ? prev.filter(x => x !== id)
    : [...prev, id]
  );
}, []);

// REQUIRED: Derived state without effects
function FindingsDisplay({ findings }: { findings: Finding[] }) {
  // ✅ Derive during render, not in useEffect
  const criticalCount = findings.filter(f => f.severity === 'CRITICAL').length;
  const hasCritical = criticalCount > 0;

  // ...
}
```

### 13.3 Type Safety Standards

#### A. TypeScript Configuration

```jsonc
// tsconfig.json - REQUIRED SETTINGS
{
  "compilerOptions": {
    "strict": true,                    // MANDATORY
    "noImplicitAny": true,             // MANDATORY
    "strictNullChecks": true,          // MANDATORY
    "noUncheckedIndexedAccess": true,  // MANDATORY
    "exactOptionalPropertyTypes": true, // RECOMMENDED
    "noImplicitReturns": true,         // RECOMMENDED
    "noFallthroughCasesInSwitch": true // RECOMMENDED
  }
}
```

#### B. Type Definitions

```typescript
// types/finding.ts - REQUIRED TYPE DEFINITIONS

export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';

export type Category =
  | 'PORT_EXPOSURE'
  | 'AUTHENTICATION'
  | 'CREDENTIALS'
  | 'CONFIGURATION'
  | 'PERMISSIONS'
  | 'NETWORK';

export interface Finding {
  readonly id: string;
  readonly title: string;
  readonly description: string;
  readonly severity: Severity;
  readonly category: Category;
  readonly cvssScore: number;
  readonly location?: string;
  readonly remediation: RemediationStep[];
  readonly references?: string[];
}

export interface RemediationStep {
  readonly step: number;
  readonly instruction: string;
  readonly code?: string;
  readonly filePath?: string;
}

export interface ScanResult {
  readonly findings: readonly Finding[];
  readonly systemInfo: SystemInfo;
  readonly scanTime: string;
  readonly overallRiskScore: number;
  readonly riskLevel: RiskLevel;
}

export type RiskLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'SAFE';
```

#### C. IPC Type Safety

```typescript
// types/ipc.ts - REQUIRED IPC TYPES

export interface IPCChannels {
  'scanner:start': {
    args: [modules: string[]];
    return: void;
  };
  'scanner:progress': {
    args: [progress: ScanProgress];
    return: void;
  };
  'scanner:result': {
    args: [result: ScanResult];
    return: void;
  };
  'scanner:cancel': {
    args: [];
    return: boolean;
  };
  'export:generate': {
    args: [format: ExportFormat, options: ExportOptions];
    return: string; // File path
  };
}

export type ExportFormat = 'html' | 'json' | 'markdown' | 'pdf';

// Type-safe IPC invoke wrapper
export function invokeIPC<K extends keyof IPCChannels>(
  channel: K,
  ...args: IPCChannels[K]['args']
): Promise<IPCChannels[K]['return']> {
  return window.electron.invoke(channel, ...args);
}
```

### 13.4 Memory Leak Prevention

#### A. Common Leak Sources & Prevention

| Leak Source | Prevention Pattern |
|-------------|-------------------|
| Event listeners | Always remove in useEffect cleanup |
| Timers | Clear in useEffect cleanup |
| IPC subscriptions | Return unsubscribe function, call on unmount |
| Large scan results | Clear from state when navigating away |
| Closures | Avoid capturing large objects in callbacks |

#### B. Required Cleanup Pattern

```typescript
// MANDATORY PATTERN for all components with subscriptions
function ScanProgress() {
  const [progress, setProgress] = useState<ScanProgress | null>(null);

  useEffect(() => {
    // Store cleanup functions
    const cleanups: (() => void)[] = [];

    // IPC subscription
    const unsubProgress = window.scanner.onProgress(setProgress);
    cleanups.push(unsubProgress);

    // Timer (if needed)
    const timerId = setInterval(checkStatus, 1000);
    cleanups.push(() => clearInterval(timerId));

    // REQUIRED: Cleanup on unmount
    return () => {
      cleanups.forEach(cleanup => cleanup());
    };
  }, []);

  return <ProgressDisplay progress={progress} />;
}
```

#### C. Store Cleanup

```typescript
// stores/scanStore.ts - REQUIRED CLEANUP METHODS
import { create } from 'zustand';

interface ScanStore {
  findings: Finding[];
  scanResult: ScanResult | null;

  // Actions
  setFindings: (findings: Finding[]) => void;
  setScanResult: (result: ScanResult) => void;

  // REQUIRED: Cleanup method
  reset: () => void;
}

export const useScanStore = create<ScanStore>((set) => ({
  findings: [],
  scanResult: null,

  setFindings: (findings) => set({ findings }),
  setScanResult: (result) => set({ scanResult: result }),

  // REQUIRED: Clear large data when not needed
  reset: () => set({ findings: [], scanResult: null }),
}));
```

### 13.5 Security Standards

#### A. Electron Security Checklist

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| Disable Node integration | nodeIntegration: false in webPreferences | REQUIRED |
| Enable context isolation | contextIsolation: true in webPreferences | REQUIRED |
| Use preload scripts | Expose minimal API via contextBridge | REQUIRED |
| Validate IPC inputs | Sanitize all data from renderer process | REQUIRED |
| Disable remote module | Never use @electron/remote | REQUIRED |
| CSP headers | Set strict Content-Security-Policy | REQUIRED |

```typescript
// electron/main.ts - REQUIRED SECURITY CONFIG
const mainWindow = new BrowserWindow({
  webPreferences: {
    nodeIntegration: false,        // MANDATORY
    contextIsolation: true,        // MANDATORY
    sandbox: true,                 // MANDATORY
    preload: path.join(__dirname, 'preload.js'),
    webSecurity: true,             // MANDATORY
  },
});

// Set CSP
mainWindow.webContents.session.webRequest.onHeadersReceived((details, callback) => {
  callback({
    responseHeaders: {
      ...details.responseHeaders,
      'Content-Security-Policy': [
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';"
      ],
    },
  });
});
```

#### B. IPC Security

```typescript
// electron/main.ts - REQUIRED INPUT VALIDATION
import { ipcMain } from 'electron';
import { z } from 'zod';

// Define validation schemas
const StartScanSchema = z.object({
  modules: z.array(z.enum(['port', 'credential', 'config', 'process', 'permission', 'network'])),
});

ipcMain.handle('scanner:start', async (event, args) => {
  // REQUIRED: Validate input
  const result = StartScanSchema.safeParse({ modules: args });
  if (!result.success) {
    throw new Error(`Invalid input: ${result.error.message}`);
  }

  // Proceed with validated data
  return startScan(result.data.modules);
});
```

#### C. Data Sanitization

```typescript
// utils/sanitize.ts - REQUIRED FOR ALL USER-FACING DATA
import DOMPurify from 'dompurify';

// Sanitize HTML content before rendering
export function sanitizeHtml(dirty: string): string {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'code', 'pre'],
    ALLOWED_ATTR: [],
  });
}

// Mask sensitive data in findings
export function maskCredential(value: string): string {
  if (value.length <= 8) return '***';
  return `${value.slice(0, 4)}...${value.slice(-4)}`;
}
```

### 13.6 Anti-Patterns to AVOID

| Anti-Pattern | Why It's Bad | Correct Approach |
|--------------|--------------|------------------|
| Synchronous IPC | Blocks UI thread completely | Use async invoke() |
| Eager module loading | Slow startup, high memory | Lazy load on demand |
| Inline object props | Causes unnecessary re-renders | Memoize with useMemo |
| Barrel file imports | Increases bundle size | Direct imports |
| `any` type | Loses type safety | Explicit types or `unknown` |
| Missing cleanup | Memory leaks | Always return cleanup function |
| Direct Node API in renderer | Security vulnerability | Use preload + contextBridge |
| Storing passwords/keys | Security risk | Never store, let user input |

### 13.7 Performance Budgets

| Metric | Target | Maximum |
|--------|--------|---------|
| App startup | < 2s | 3s |
| Time to interactive | < 1.5s | 2.5s |
| Scan progress update latency | < 100ms | 200ms |
| Finding card expand | < 50ms | 100ms |
| Bundle size (renderer) | < 500KB | 1MB |
| Memory usage (idle) | < 100MB | 150MB |
| Memory usage (during scan) | < 200MB | 300MB |

### 13.8 Code Review Checklist

Before merging any PR, verify:

**TypeScript:**

- [ ] No `any` types (use `unknown` if needed)
- [ ] All function parameters have explicit types
- [ ] All return types are explicit
- [ ] strictNullChecks violations fixed

**React:**

- [ ] No inline object/array props without memoization
- [ ] Event handlers use useCallback with correct deps
- [ ] List items are memoized with memo()
- [ ] No derived state in useEffect (derive during render)

**Electron:**

- [ ] No synchronous IPC calls
- [ ] All IPC inputs validated with Zod
- [ ] Preload script uses contextBridge only
- [ ] No direct Node API access in renderer

**Memory:**

- [ ] All event listeners cleaned up
- [ ] All timers cleared on unmount
- [ ] Large data structures cleared when not needed

**Security:**

- [ ] User input sanitized before display
- [ ] No credentials stored or logged
- [ ] CSP headers configured
- [ ] Node integration disabled

---

## 14. Implementation Verification

### 14.1 Automated Checks

```bash
# Required CI/CD checks
npm run typecheck          # TypeScript strict mode
npm run lint               # ESLint with React rules
npm run test               # Jest unit tests
npm run test:e2e           # Playwright E2E tests
npm run bundle-analyze     # Check bundle size
```

### 14.2 Manual Verification

**Startup Performance**

- Cold start app, measure time to interactive
- Verify no console errors on startup

**Memory Profile**

- Open DevTools → Memory tab
- Take heap snapshot at idle
- Run full scan
- Take heap snapshot after results displayed
- Navigate away, take snapshot (should return to baseline)

**IPC Security**

- Verify `window.require` is undefined in renderer
- Verify `window.process` is undefined in renderer
- Test invalid IPC inputs are rejected