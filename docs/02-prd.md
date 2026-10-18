# CP-M2: Product Requirements Document: Adverse

**Course:** IST 300 · Building Software with Agentic AI
**Author:** Alex Caraballo
**Product:** Adverse
**Status:** Draft v1. Requirements are based on regulatory research and my prototype, not yet on user interviews. Anything marked *(assumption)* needs to be confirmed with real users.

---

## 1. Problem

Companies use outside AI tools to screen job applicants. When a rejected candidate sues or a regulator asks questions, the company's in-house employment lawyer has to show what the AI actually did: what it saw, what it decided, and how it was configured at that moment.

Today, the only record of that comes from the AI vendor or from the company's own hiring system. Both have a stake in the outcome, both can change their data, and neither was built to be evidence. Recent cases like *Mobley v. Workday* and *Kistler v. Eightfold* show that AI hiring vendors and the companies using them are now being challenged in court over screening decisions.

## 2. Product in one sentence

Adverse is an independent, tamper-evident record of every AI hiring decision, like a dashcam for AI screening, so an in-house lawyer can prove what happened without relying on the vendor.

## 3. Users

| User | What they need from Adverse |
|------|-----------------------------|
| **In-house employment lawyer** (primary) | A trustworthy record of any single AI decision that they can pull up, show to others, and defend. |
| **People Ops / HR admin** (e.g., the person who configures the vendor tool) | Their configuration choices recorded accurately, so they aren't blamed for settings they didn't make. |
| **Outside counsel** | Temporary, limited access to specific records during a dispute. |

Rejected candidates are **not** a v1 user. *(Decision: Adverse's buyer is the company. Candidate access is a Won't for v1.)*

## 4. Goals and non-goals

**Goals**
- Every AI screening decision gets captured and sealed automatically, with no one choosing what gets saved.
- A lawyer can open any decision and see what the model saw, what it decided, and how it was configured.
- Anyone can verify that a record hasn't been changed, without trusting Adverse.

**Non-goals (v1)**
- Adverse does not judge whether a decision was fair or legal. It records; lawyers judge.
- Adverse does not use AI to summarize, explain, or rewrite any decision.
- No mobile app.
- No candidate-facing portal.
- No bias auditing or compliance scoring.

## 5. Requirements

These are the "what would have to be true" requirements from my D06 Discovery Log. CP-M3 traces each architecture component back to these IDs.

| ID | Requirement |
|----|-------------|
| R1 | Adverse captures the vendor's decision as it's sent to the company's hiring system, instead of relying on the vendor to send a separate copy. |
| R2 | If Adverse is down, hiring keeps working. Decisions made during the outage are still captured once Adverse is back, and marked as sealed late. |
| R3 | Each record is sealed at the moment of capture, before anyone can change it. |
| R4 | The resume the model saw is kept for at least 4 years and can be checked against the version captured. |
| R5 | The vendor's explanation is stored word for word. Adverse never generates or paraphrases it. |
| R6 | The vendor's model version and settings at the time of each decision are recorded, and any change to those settings is recorded with who made it and when. |
| R7 | A copy of each record's fingerprint is kept outside Adverse, so tampering with Adverse itself would be detectable. |
| R8 | Every time someone opens a record, it's logged at the moment they open it. Nobody, including Adverse staff, can edit or delete the log. |

## 6. User stories

### Must (MVP slice)

**S1. View a decision record**
As an in-house employment lawyer, I want to open a single AI hiring decision and see what the model saw, what it decided, and how it was configured, so that I can understand and defend that decision.
- Given a captured decision, when I open its record, then I see the applicant reference, job, decision, score, threshold, capture time, model version, and settings fingerprint on one screen.
- The vendor explanation is shown exactly as the vendor sent it, labeled "Verbatim from vendor response."
- If the record was sealed late (R2), the screen says so and shows both the original capture time and the seal time.

**S2. Automatic capture**
As an in-house lawyer, I want every screening decision captured automatically as it happens, so that no one at the vendor or my company can choose what gets recorded.
- Every response the vendor sends to the hiring system results in exactly one record.
- No user can create, edit, or delete a record by hand.
- If Adverse is unavailable, the hiring system still receives the vendor's response with no added delay. *(Decided: Adverse never blocks hiring.)*

**S3. Verify a record hasn't changed**
As an in-house lawyer, I want to prove a record hasn't been altered since capture, so that opposing counsel can't argue it was edited.
- Each record shows its seal and whether it currently verifies.
- If any part of the record no longer matches its seal, the record is shown as "Failed verification," never hidden.
- A third party can verify the record without an Adverse account. *(See Open Questions on exactly how.)*

**S4. See who opened a record**
As an in-house lawyer, I want a read-only access log on each record, so that I can show exactly who saw it and when.
- Opening a record adds an entry with the person's name, role, and time, before the record is shown.
- Denied attempts are also logged.
- No one can edit or delete log entries, including admins.

### Should

**S5. Share a record with outside counsel**
As an in-house lawyer, I want to give outside counsel access to specific records, so that they can work on a dispute without seeing everything.
- I can grant access to one or more specific records.
- Access ends automatically on an expiration date I set. *(Decided: access expires on its own; I can also remove it early.)*
- Granting and removing access both appear in the access log.

**S6. Configuration history**
As a People Ops admin, I want a history of the vendor's settings over time, so that it's clear what settings were in effect for any decision and who changed them.
- Each record links to the settings that were in effect when it was captured.
- Each settings change shows the old value, new value, who changed it, and when.

### Could

**S7. Export a record**
As an in-house lawyer, I want to export a record as a PDF, so that I can include it in a legal filing or share it offline.
- The export includes everything on the record screen, plus the seal and the information needed to verify it.

### Won't (v1)
- Candidate portal or candidate access to records
- AI-generated summaries or explanations
- Mobile app
- Support for screening vendors other than one pilot vendor *(assumption: start with one vendor integration)*

## 7. Success measures

- 100% of vendor responses during a pilot have a matching sealed record.
- 0 records that fail verification in normal operation.
- A lawyer can find and open a specific decision in under 1 minute. *(assumption)*
- At least one in-house lawyer says they would use an Adverse record in a real dispute. *(needs interviews)*

## 8. Open questions (parked)

- **Will companies route live vendor traffic through Adverse?** S2 depends on it. If not, the fallback is a vendor-sent copy, which weakens R1. Needs customer interviews.
- **How long must records be kept?** 4 years is my working minimum. The real number depends on the laws that apply, which I need to confirm with an employment attorney.
- **How does a third party verify a record without Adverse?** Needed for S3. This is a design question for CP-M3.
- **Who at a customer company is allowed to see which records by default?**
- **What happens when a candidate requests deletion of their data?** Conflicts with retention. Needs legal input.

## 9. What I haven't validated

My requirements come from legal research (court cases and state AI hiring laws) and my own prototype, not from interviews with in-house lawyers. The biggest risk in this PRD is that I'm solving the problem I think lawyers have instead of the one they actually have. Next step is talking to at least three in-house employment lawyers before building past the MVP slice.
