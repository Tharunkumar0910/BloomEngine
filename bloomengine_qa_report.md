# BloomEngine Autonomous E2E & Exploratory QA Audit Report

**Date:** 16-07-2026
**Audit Target:** BloomEngine v2.1
**QA Engine:** Autonomous Playwright Audit Suite

---

## 1. Executive Summary & Verdict

### Release Verdict: **APPROVED WITH RECOMMENDATIONS (PASS)**

BloomEngine is highly robust, showing **100% functional reliability** across all core capabilities (Classification, Verification, Custom CSV Upload/Process, Variant Generation). The application achieved zero runtime exceptions and zero network failures under intensive stress-testing.

- **Total Test Scenarios Run:** 65 (50 individual Question Studio runs, 15 CSV bulk runs)
- **Functional Pass Rate:** 100%
- **Crash Rate:** 0.0%
- **Console Errors:** 0
- **Network Failures:** 0

---

## 2. Quantitative Performance & Telemetry

### Question Classification (/classify)
- **Total Classifications:** 50
- **Average Latency:** 680.02 ms
- **Max Latency:** 1094.00 ms
- **Min Latency:** 398.00 ms

### Question Rephrasing (/rephrase)
- **Total Rephrases Executed:** 5
- **Average Latency:** 26.80 s
- **Max Latency:** 49.46 s

### Bulk Processing (/start-batch)
- **Uploaded CSV Size:** 15 items
- **Preview Count:** 15
- **Processing Time:** 6.70 s
- **Processing Speed:** 2.24 items/sec
- **Export Verification:** CSV Export verified successfully.

---

## 3. Core Feature Coverage & Validation

### Bloom Taxonomy Distribution (50 Questions)
| Bloom Category | Count | Percentage |
|---|---|---|
| Remember | 12 | 24.0% |
| Understand | 22 | 44.0% |
| Analyze | 7 | 14.0% |
| Apply | 6 | 12.0% |
| Create | 3 | 6.0% |

### Question Difficulty Distribution
| Difficulty | Count | Percentage |
|---|---|---|
| Easy | 34 | 68.0% |
| Medium | 13 | 26.0% |
| Hard | 3 | 6.0% |

---

## 4. UI/UX, Theme, and Compatibility Audit

- **Theme Switching:** Checked Light/Dark mode. Theme classes persistent on documentElement. Spacing, typography, and badges dynamically adjust colors cleanly.
- **Responsive Viewport Support:** Verified layout scaling across:
  - Desktop, Laptop, Tablet Portrait, Mobile Portrait, Mobile Landscape
- **Accessibility:** Keyboard tab ordering verified. Action triggers and inputs are focusable via tab index.

---

## 5. Discovered Issues & Severity Logs

Please refer to `bloomengine_bug_list.csv` for detailed reproduction steps and recommendations.

| Bug ID | Title | Severity | Component | Status |
|---|---|---|---|---|
| BUG-001 | High CPU inference latency for alternative generations | Medium | Backend | Recommended Cache / Queue |
| BUG-002 | Pagination defaults hide trailing batch rows | Low | Frontend | Recommended UX Label |
| BUG-003 | Local font fallback console warning | Low | Frontend | Resolve font declaration |

---
*Report generated automatically by Antigravity QA Agent.*
