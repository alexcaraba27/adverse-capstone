# Adverse — Product Backlog

**Product:** Adverse is an independent third-party record of what an AI screening tool did when it evaluated a job applicant — a "dashcam" for AI hiring decisions.

**Primary users:**
- In-house employment lawyers at companies that use outside AI screening vendors.
- Rejected candidates who want proof of what happened that doesn't depend on the vendor or the employer.

> **Note on confidence:** No user interviews have been conducted yet. Items marked **[GUESS]** are unverified assumptions about user needs, regulatory requirements, or workflows that need validation before building.

---

## MVP Slice

The MVP is the set of **Must** stories below (Stories 1, 2, and 7). Together they deliver the minimum promise of the product: an independent, retrievable, defensible record of a single AI screening decision, accessible to both sides.

---

## User Stories

### Story 1 — Retrieve a tamper-evident decision log
**As an** in-house employment lawyer,
**I want** to pull a tamper-evident log of what the AI screening tool did for a specific applicant,
**so that** I can defend a hiring decision without having to trust the vendor's own records.

**Acceptance criteria:**
- Log includes timestamp, vendor model identifier/version, inputs the model received, and the output score or recommendation.
- Log is cryptographically signed at capture time and independently verifiable without contacting the vendor.
- Retrievable by applicant identifier in under 10 seconds. **[GUESS — latency target not validated]**

**Priority:** Must *(MVP)*

---

### Story 2 — Candidate requests their own evaluation record
**As a** rejected candidate,
**I want** to request a copy of how the AI evaluated my application,
**so that** I have proof of what happened that doesn't depend on the employer or vendor.

**Acceptance criteria:**
- Candidate can authenticate using information they provided on the original application (e.g., email + application reference). **[GUESS — auth model not validated with candidates or counsel]**
- Request is fulfilled within 7 days. **[GUESS — assumed from analogy to FCRA/GDPR SAR timelines; actual requirement unconfirmed]**
- Delivered report describes, in plain language, what the AI considered and what it output.

**Priority:** Must *(MVP)*

---

### Story 7 — Produce a complete audit trail for a regulator
**As an** in-house employment lawyer,
**I want** to export the full audit trail of AI touchpoints for a specific candidate,
**so that** I can respond to an EEOC inquiry, NYC Local Law 144 audit, or similar regulatory request.

**Acceptance criteria:**
- Export includes every AI interaction tied to that candidate (screening, re-scoring, ranking changes).
- Chain-of-custody metadata is preserved and visible in the export.
- Output format is acceptable for regulatory submission. **[GUESS — no confirmed format standard; needs validation with employment counsel]**

**Priority:** Must *(MVP)*

---

### Story 3 — Disparate-impact monitoring across protected classes
**As an** in-house employment lawyer,
**I want** to see outcome rates of the AI screener broken down by protected class,
**so that** I can spot disparate impact risk before it becomes litigation.

**Acceptance criteria:**
- Dashboard shows selection/rejection rates by self-reported demographic categories.
- Four-fifths rule threshold crossings are visibly flagged.
- Report is exportable as PDF for internal legal review. **[GUESS — export format preference unvalidated]**

**Priority:** Should

---

### Story 4 — Explain the decision to the candidate
**As a** rejected candidate,
**I want** to see which factors most influenced the AI's negative decision about me,
**so that** I can decide whether to appeal, request correction, or file a complaint.

**Acceptance criteria:**
- Report names the top factors that pushed the score down, in plain English (not model internals or feature IDs).
- Explanation distinguishes between factors the candidate provided vs. inferred factors. **[GUESS — assumes candidates care about this distinction; needs interview]**

**Priority:** Should

---

### Story 8 — Candidate downloads a portable dossier
**As a** rejected candidate,
**I want** to download my full Adverse dossier in a portable format,
**so that** I can share it with an attorney or an advocacy organization.

**Acceptance criteria:**
- Export available in both human-readable PDF and machine-readable JSON.
- Export includes the Adverse verification signature so a third party can confirm authenticity.

**Priority:** Should

---

### Story 5 — Alert when the vendor's model changes
**As an** in-house employment lawyer,
**I want** to be alerted when the screening vendor pushes a new model version,
**so that** I can reassess legal risk if behavior shifts.

**Acceptance criteria:**
- Alert fires within 24 hours of a detected version change. **[GUESS — latency target not validated]**
- Alert includes a summary of behavior drift on a stored canary set of past applicants.

**Priority:** Could

---

### Story 6 — Candidate files a correction/dispute
**As a** rejected candidate,
**I want** to attach a formal correction or dispute to my decision record,
**so that** there is a documented challenge on file if the AI used wrong information about me.

**Acceptance criteria:**
- Dispute is permanently attached to the original signed decision log without altering it.
- The employer is notified of the dispute within 48 hours. **[GUESS — SLA and whether employers want this notification at all is unvalidated]**

**Priority:** Could

---

## Summary

| # | Story | Priority | MVP |
|---|---|---|---|
| 1 | Lawyer retrieves tamper-evident decision log | Must | ✓ |
| 2 | Candidate requests own evaluation record | Must | ✓ |
| 7 | Lawyer produces regulator-ready audit trail | Must | ✓ |
| 3 | Disparate-impact monitoring dashboard | Should | |
| 4 | Candidate-facing decision explanation | Should | |
| 8 | Candidate downloads portable dossier | Should | |
| 5 | Alert on vendor model change | Could | |
| 6 | Candidate files correction/dispute | Could | |
