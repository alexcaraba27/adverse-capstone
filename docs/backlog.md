# Adverse — Product Backlog

**Product:** Adverse is a dashcam for AI hiring. When a company's outside AI screening tool evaluates a job applicant, Adverse freezes an independent record of what the AI saw, what it decided, when, which model version and settings produced the decision, and who configured those settings.

**Primary user:** The company's in-house employment lawyer, who has to sign off on vendor AI they can't see into.
**Secondary user:** The rejected candidate.

**Hard product constraint:** No AI ever creates or changes a record. Records are written by deterministic capture at decision time and modified by no one afterward.

> **Confidence note:** No in-house employment lawyers have been interviewed yet. Items marked **[GUESS]** are unverified assumptions about workflows, authentication, regulatory expectations, or latency/SLA needs that must be validated before building.

---

## MVP Slice

The MVP is the set of **Must** stories below (Stories 1, 2, and 3). Together they deliver the minimum promise of the product: a lawyer can open a single frozen decision record, trust it hasn't been altered, and the candidate it describes can get their own copy.

---

## User Stories

### Story 1 — Lawyer opens a single decision record
**As an** in-house employment lawyer,
**I want** to open the full record of a single AI screening decision for one applicant,
**so that** I can see exactly what the vendor's AI did without having to ask the vendor.

**Acceptance criteria:**
- Record displays the inputs the AI received, the decision/output it produced, the exact timestamp, the model version and settings in effect, and the identity of the person who configured those settings.
- Record is retrievable by candidate identifier or decision identifier in under 10 seconds. **[GUESS — latency target not validated with lawyers]**
- The record is read-only in the UI, and every access is itself logged.

**Priority:** Must *(MVP)*

---

### Story 2 — Frozen, tamper-evident capture
**As an** in-house employment lawyer,
**I want** each decision record to be frozen at the moment of capture and verifiably unaltered,
**so that** I can rely on it as evidence even if the vendor or an internal team later tries to revise history.

**Acceptance criteria:**
- Each record is cryptographically signed at capture time; signature is verifiable without contacting the vendor.
- Any attempt to modify a record is rejected and the attempt itself is logged.
- No AI system or model is permitted to write, edit, or regenerate a record — enforced in code, not by policy. **[GUESS — assumes lawyers care about this guarantee being technical rather than contractual]**

**Priority:** Must *(MVP)*

---

### Story 3 — Candidate requests their own decision record
**As a** rejected candidate,
**I want** to request the record of how the AI evaluated me,
**so that** I have independent proof of what happened without needing cooperation from the employer or the vendor.

**Acceptance criteria:**
- Candidate can authenticate using information from their original application (e.g., email + application reference). **[GUESS — auth model unvalidated; verifying candidates without employer cooperation is an open design question]**
- Delivered record is readable by a non-lawyer and clearly identifies the model version, timestamp, and inputs considered.
- Request is fulfilled within 7 days. **[GUESS — assumed by analogy to FCRA/GDPR SAR timelines; no confirmed legal requirement]**

**Priority:** Must *(MVP)*

---

### Story 4 — Export a decision record for outside counsel or a regulator
**As an** in-house employment lawyer,
**I want** to export a single decision record as a self-contained file,
**so that** I can hand it to outside counsel or a regulator and they can verify it independently.

**Acceptance criteria:**
- Export bundles the record, its signature, and the verification material needed to check it offline.
- Export is produced in both a human-readable format (PDF) and a machine-readable format (JSON). **[GUESS — format preference not confirmed with employment counsel]**
- Chain-of-custody metadata (who exported it, when) is embedded in the export.

**Priority:** Should

---

### Story 5 — See the configuration-change history for a vendor model
**As an** in-house employment lawyer,
**I want** to see a timeline of changes to the vendor model's settings and who made each change,
**so that** when I sign off on continued use of the vendor, I know what has shifted since the last review.

**Acceptance criteria:**
- Timeline shows every settings change with timestamp and the identity of the configurer.
- Each entry links to the decision records produced under that configuration.
- A diff view shows what changed between two configurations. **[GUESS — assumes lawyers want diffs rather than full-config snapshots]**

**Priority:** Should

---

### Story 6 — Search and filter decision records
**As an** in-house employment lawyer,
**I want** to filter decision records by model version, date range, and outcome,
**so that** I can scope a review to a specific vendor change or incident window.

**Acceptance criteria:**
- Filters can be combined (e.g., model v2.3 AND rejected AND Q2 2026).
- Result set shows counts and is exportable as a list of record identifiers.
- Each result links to the full Story 1 record view.

**Priority:** Should

---

### Story 7 — Alert on vendor model or settings change
**As an** in-house employment lawyer,
**I want** to be notified when the vendor pushes a new model version or changes model settings,
**so that** I can decide whether my prior sign-off still holds.

**Acceptance criteria:**
- Alert fires within 24 hours of a detected change. **[GUESS — SLA not validated]**
- Alert names what changed and who made the change.
- Alert links directly to the configuration-change timeline (Story 5).

**Priority:** Could

---

### Story 8 — Candidate attaches a dispute to their record
**As a** rejected candidate,
**I want** to attach a written dispute to the record of my decision,
**so that** my objection is formally on file alongside the AI's decision.

**Acceptance criteria:**
- Dispute is appended as a separate signed artifact; the original record is not modified.
- The in-house lawyer is notified that a dispute has been attached. **[GUESS — unclear whether lawyers want this notification or would prefer it suppressed]**

**Priority:** Could

---

## Summary

| # | Story | Priority | MVP |
|---|---|---|---|
| 1 | Lawyer opens a single decision record | Must | ✓ |
| 2 | Frozen, tamper-evident capture | Must | ✓ |
| 3 | Candidate requests their own decision record | Must | ✓ |
| 4 | Export a record for outside counsel / regulator | Should | |
| 5 | Configuration-change history for a vendor model | Should | |
| 6 | Search and filter decision records | Should | |
| 7 | Alert on vendor model or settings change | Could | |
| 8 | Candidate attaches a dispute to their record | Could | |
