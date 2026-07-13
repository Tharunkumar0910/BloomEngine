# BloomAI Arena UX/UI Redesign Specification

## Executive Summary
This document outlines the complete UX/UI redesign strategy for BloomAI Arena. Acting as a blueprint for the next-generation Figma design, it reimagines the existing architecture into a cohesive, AI-first workspace akin to modern platforms like Linear, Notion AI, and Cursor. The goal is to reduce cognitive overload, unify fragmented workflows, and deliver a premium, fast, and intuitive experience suitable for researchers and educational institutions.

---

## Phase 1: User Journey Analysis

### 1. Teacher / Educator
- **Goals:** Quickly generate varied assessment questions, ensure topic relevance, and manage a bank of verified questions.
- **Pain Points:** Overwhelmed by deep technical classifier metrics; generating questions one-by-one is tedious.
- **Most Used Features:** Studio (Generation), Bulk Processing (Question Management).

### 2. Researcher / AI Engineer
- **Goals:** Analyze model drift, evaluate FLAN-T5 topic preservation, and benchmark DeBERTa confidence scores.
- **Pain Points:** Disconnected workflow between bulk generation and analytics; hard to compare specific prompt variants side-by-side.
- **Most Used Features:** Analytics, Bulk Processing, System Models.

### 3. Student / End User
- **Goals:** Engage with the output of the generated assessments (though primarily a consumer outside the core platform, their experience dictates quality requirements).
- **Pain Points:** Irrelevant or poorly phrased generated questions.
- **Most Used Features:** Indirectly interacts with generated outputs.

### 4. Content Creator / Curriculum Designer
- **Goals:** Curate high-quality, tagged, and standardized content across multiple domains (e.g., Cloud, Network, DB).
- **Pain Points:** Lack of robust organization (tags, folders, notes) inside the legacy bulk processor.
- **Most Used Features:** Bulk Processing (Tagging, Review Status), Studio.

### 5. Administrator
- **Goals:** Monitor system health, API latency, export data, and manage user/model access.
- **Pain Points:** Fragmented dashboard lacking actionable health metrics.
- **Most Used Features:** Dashboard, Export functionality.

---

## Phase 2: Information Architecture

The current navigation is fragmented. We will introduce a clear primary, secondary, and utility hierarchy.

### Primary Navigation (Left Sidebar - Collapsible)
- **Home (Dashboard)**: System health and high-level activity.
- **Workspace (formerly Studio & Bulk Processing)**: The unified center for single and bulk question management.
- **Analytics**: Deep-dive reporting and performance metrics.
- **Models & Prompts**: Management of underlying DeBERTa/FLAN-T5 models, prompt histories, and system config.

### Secondary Navigation (Contextual Top Bar)
- **Breadcrumbs**: e.g., `Workspace / Introduction to Cloud Computing / Variant Review`
- **Global Search**: `CMD + K` to search across questions, tags, and metrics.
- **View Toggles**: Switch between `Table View`, `Kanban View` (by Status), and `Split View`.

### Quick Actions & Command Palette
- **Command Palette (`CMD + K`)**: Instantly trigger actions like "Generate Variant," "Export to CSV," or "Navigate to Analytics."

---

## Phase 3: Dashboard Redesign

The Dashboard transitions from a static landing page to a proactive command center.

### Layout / Wireframe
- **Top Row (KPIs):** System Health Status (Green/Yellow/Red), Questions Processed (24h/Total), Average Bloom Accuracy, Average Topic Preservation.
- **Center Left (Activity Feed):** Real-time feed of reviewer actions (e.g., "John approved 45 questions", "System flagged 12 variants for drift").
- **Center Right (Quick Actions):** One-click buttons to "Create New Question", "Import CSV", or "View Failing Benchmarks."
- **Bottom Row (Model Status):** Mini sparkline charts showing inference latency for DeBERTa-v3 and FLAN-T5.

---

## Phase 4: Studio Redesign (The Unified Workspace)

The Studio evolves into a powerful split-pane IDE-style environment.

### Layout / Wireframe
- **Left Panel (Input & Context):**
  - **Question Input:** Auto-expanding markdown textarea.
  - **Context/Tags:** Inline inputs for assigning domain tags and reviewer notes before generation.
- **Center Panel (Classification Engine):**
  - **Live Results:** Dynamic Bloom and Difficulty badges.
  - **Confidence Meter:** A sleek, circular or linear progress bar with detailed AI Explanation below.
- **Right Panel (Generation & Variants):**
  - **Variant Stack:** Stacked cards representing Easy, Moderate, and Difficult variants.
  - **Comparison View:** Side-by-side diffing of concepts preserved/lost.
- **Bottom Bar (Diagnostics):** Sticky footer displaying inference time, model version, and API status.

### Interaction Flow
Typing in the Left Panel auto-debounces to the Center Panel. Hitting "Generate" spawns skeletons in the Right Panel that smoothly fade into the generated variants. 

---

## Phase 5: Bulk Processing Redesign (Question Management)

Transitioning from a basic data table to a modern CRM-style workspace (e.g., Linear).

### Layout / Wireframe
- **Header:** Title, Export Buttons, Global Search, and Filter Dropdowns.
- **Main Table:**
  - **Columns:** Checkbox, ID, Question (truncated), Status Badge, Tags, Bloom, Difficulty.
  - **Interactions:** Multi-select for bulk tagging, approval, or deletion.
- **Right-side Drawer (Sliding Panel):**
  - Opens on row click.
  - Contains full record details, interactive Notes and Tags inputs.
  - Integrated variant generation buttons and history, keeping the user in context without losing their place in the table.

---

## Phase 6: Analytics Redesign

A transition toward actionable, drill-down reporting.

### Layout / Wireframe
- **Hero KPI Cards:** Exact Match Rate, Topic Preservation %, Average Confidence.
- **Top Charts (Distribution):**
  - **Bloom Distribution:** Clean Donut Chart with modern tooltips.
  - **Difficulty Distribution:** Stacked Bar Chart comparing Requested vs. Generated.
- **Bottom Charts (Trends & Health):**
  - **Accuracy Trends over Time:** Line chart (smoothed) showing system improvement.
  - **Topic Drift Analysis:** Radar chart or heat map showing which domains suffer the most hallucination.
- **Focused Context Card:** Deep-linked from the Workspace Drawer, highlighting a specific question's metrics against global averages.

---

## Phase 7: Design System

To ensure consistency and a premium feel, the design system must be strictly adhered to.

- **Typography Scale:** 
  - Primary: `Inter` or `Geist` for exceptional readability. 
  - Monospace (for IDs/Code): `JetBrains Mono` or `Fira Code`.
- **Spacing System:** Base-8 scale (8px, 16px, 24px, 32px, etc.).
- **Color System:**
  - *Backgrounds:* Very dark slate (`#0F1117`) for dark mode, crisp white for light mode.
  - *Accents:* Primary Indigo (`#6366F1`) for primary actions.
  - *Status:* Emerald (`#10B981`) for Verified/Success, Amber (`#F59E0B`) for Review/Adjacent, Rose (`#F43F5E`) for Rejected/Mismatch.
- **Component Library Highlights:**
  - **Buttons:** Ghost, Outline, and Solid variants with micro-interactions (scale on click).
  - **Cards:** Subtle 1px borders with soft drop shadows (glassmorphism accents in dark mode).
  - **Drawers:** Smooth `cubic-bezier(0.4, 0, 0.2, 1)` transitions.
  - **Badges:** Pill-shaped, low opacity background with high opacity text for status indicators.

---

## Phase 8: AI Experience Improvements

- **AI Copilot:** A floating command bar `CMD + J` to ask the AI to "Tag all networking questions" or "Find questions with low confidence."
- **Inline Suggestions:** Gray placeholder text predicting the end of a question as the user types.
- **Variant Comparison View:** A visual "diff" highlighting exactly which words were changed, added, or removed from the original question.
- **Prompt History:** A rewind button to see previous versions of a generated variant and the prompt that created it.

---

## Phase 9: Figma Structure

To maintain a scalable and professional Figma file, adhere to the following page hierarchy:

1. **00_Cover** - Project title, status, and lead designer.
2. **01_Foundations** - Colors, Typography, Spacing, Shadows, Grid setup.
3. **02_Components** - Master components (Buttons, Inputs, Cards, Nav, Tables) utilizing Figma Variants and Auto Layout.
4. **03_Dashboard** - High-fidelity mockups of the landing experience.
5. **04_Studio_Workspace** - The split-pane generation view and edge cases.
6. **05_Bulk_Management** - Table views, filters, and sliding drawer states.
7. **06_Analytics** - Chart components and dashboard layouts.
8. **07_Mobile_Responsive** - Adapting the table and studio for iPad/Mobile breakpoints.
9. **08_Prototypes** - Interactive click-through prototypes for user testing.
10. **09_Archive** - Old iterations and discarded concepts.

---

## Phase 10: Deliverables & Next Steps

This specification serves as the foundational architectural document for the UX/UI overhaul. The immediate next step is to hand this document to the design team to execute **Phase 9 (Figma Structure)**, beginning with the **01_Foundations** and **02_Components** libraries before moving into high-fidelity page layouts. No code changes should be initiated until the interactive prototype (Page 08) is approved by product stakeholders.
