# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **ai-console**, a Vue 3 + TypeScript frontend console application for AI/device management. The project lives in the `ai-console/` subdirectory.

## Build & Run Commands

```bash
cd ai-console
npm install        # Install dependencies
npm run dev        # Start dev server (http://localhost:5173)
npm run build       # Production build with type checking
npm run preview    # Preview production build
```

## Tech Stack

- **Framework**: Vue 3 (Composition API with `<script setup>`)
- **Language**: TypeScript (strict mode)
- **Build**: Vite 5
- **UI Library**: Element Plus 2.6
- **State**: Pinia 2.1
- **Router**: Vue Router 4.3
- **HTTP**: Axios 1.6

## Architecture

```
ai-console/src/
├── components/       # Reusable Vue components
│   ├── common/       # Generic components (DataTable, Modal, Switch, Tree, Pagination)
│   └── layout/       # Layout components (Layout, Header, Sidebar, Tabs, Breadcrumb)
├── views/            # Page components, organized by module
│   ├── super-admin/  # Menu, Resource, Microservice, UI Customize, License
│   ├── user-center/  # User, Org, Role, Operation History
│   ├── device/       # DataSource, Device, DeviceGroup, Region, SyncDevice
│   │   └── access/   # PlatformList, Gb28181, Onvif
│   ├── linkage/      # TaskEdit, LinkageRule, PushHistory
│   ├── algorithm/    # AlgorithmManage, EventManage, AlgorithmService
│   └── system/       # VideoSetting, FileManager, HelpCenter, PopupSetting, DisposeTag
├── mock/             # Mock data files mirroring view structure
├── router/           # Vue Router configuration (lazy-loaded routes)
├── stores/           # Pinia stores (currently: tabs store)
└── styles/           # Global CSS and Element Plus overrides
```

## Key Patterns

### Route Structure
- Routes are lazy-loaded via dynamic imports
- All views are nested under `/layout` with a common `Layout.vue` wrapper
- Default redirect: `/` → `/layout/super-admin/menu-manage`

### Component Naming
- PascalCase for Vue components (e.g., `DataTable.vue`, `LinkageRule.vue`)
- kebab-case for file names

### Mock Data
- Each view has a corresponding mock file in `src/mock/` that mirrors the directory structure
- Mock data uses JavaScript (`.js`) files
- `src/mock/index.js` aggregates all mocks

## Visual QA Reference

Reference screenshots are stored in `photo/`. The canonical source of truth for UI validation is `docs/screenshot-source-truth.md`.

### UI Alignment Standards (`AI_CONSOLE/UI_STANDARDS.md`)
- **A (Must Fix)**: Functional contradictions that prevent user operations
- **B (Should Fix)**: Visual semantics errors (colors, button types, hierarchy)
- **C (Consider Fix)**: Pure visual deviations (color values, spacing, font size)
- **D (Optional)**: Pixel-level differences

## Path Aliases

```typescript
// In tsconfig.json and vite.config.ts:
'@/' maps to 'ai-console/src/'
```

## Element Plus Dark Mode

The app uses Element Plus with dark CSS variables enabled:
```typescript
import 'element-plus/theme-chalk/dark/css-vars.css'
```
