# ClawdForDummies GUI

A modern React + Electron GUI for the ClawdForDummies security assessment tool.

## Features

- **Risk Dashboard** - Visual risk gauge and severity counts
- **Scan Controls** - Quick/Full scan options with module selection
- **Progress Indicator** - Real-time scan progress display
- **Findings Display** - Expandable cards grouped by severity
- **Export Panel** - HTML, JSON, Markdown report generation
- **System Info** - Collapsible system details panel

## Design

Based on a "Security Control Room" aesthetic with:
- Dark theme (`#0D1117` background)
- High-contrast severity indicators
- Color-coded findings (Critical=Red, High=Orange, Medium=Yellow, Low=Green)
- JetBrains Mono for display text, IBM Plex Sans for body text

## Tech Stack

- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **Animation**: Framer Motion
- **State**: Zustand
- **Icons**: Lucide React
- **Charts**: Recharts
- **Build**: Vite
- **Desktop**: Electron

## Development

```bash
# Install dependencies
npm install

# Start development server (web only)
npm run dev

# Start with Electron
npm run electron:dev

# Build for production
npm run build

# Build Electron app
npm run electron:build
```

## Project Structure

```
clawd-for-dummies-gui/
├── electron/           # Electron main process
├── src/
│   ├── components/     # React components
│   │   ├── common/     # Shared UI components
│   │   ├── dashboard/  # Risk dashboard
│   │   ├── export/     # Export panel
│   │   ├── findings/   # Findings display
│   │   ├── layout/     # App shell, header, footer
│   │   ├── scan/       # Scan controls
│   │   └── system/     # System info
│   ├── hooks/          # Custom React hooks
│   ├── stores/         # Zustand stores
│   ├── types/          # TypeScript types
│   └── utils/          # Utility functions
└── ...config files
```

## Integration

The GUI communicates with the Python backend via Electron IPC. The Python scanner is invoked as a subprocess and results are streamed back to the UI.
