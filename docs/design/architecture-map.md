# Adverse architecture map (MVP slice)

Every box names the requirement it serves (R1 to R8 in docs/02-prd.md). Full write-up: docs/03-architecture.md.

```mermaid
flowchart LR
    ATS["Hiring system (ATS)"]
    Vireo["Vireo (AI screening vendor)"]
    subgraph Adverse["Adverse (cloud)"]
        Capture["Capture proxy, FastAPI<br/>R1, R2"]
        Buffer[("Retry buffer<br/>R2")]
        Seal["Seal service: hash + sign<br/>R3"]
        API["Adverse API, FastAPI<br/>permission checks + access logging<br/>R8"]
        Jobs["Background jobs<br/>witness send, config check<br/>R6, R7"]
        DB[("Supabase Postgres<br/>records + access log, append-only<br/>R3, R5, R8")]
        Files[("Supabase Storage<br/>resumes, 4+ yrs<br/>R4")]
    end
    Web["Web app: lawyer record view<br/>S1, S3, S4"]
    Witness["Outside witness<br/>R7"]
    ATS -->|screening request| Capture
    Capture -->|forward| Vireo
    Vireo -->|decision| Capture
    Capture -->|unchanged response| ATS
    Capture -.->|if storage down| Buffer
    Buffer -.->|replay| Seal
    Capture --> Seal
    Seal --> DB
    Seal --> Files
    Seal --> Jobs
    Jobs --> Witness
    Jobs -->|settings check| Vireo
    Web -->|HTTPS + login| API
    API --> DB
    API --> Files
```

## Request path traced: S1 (lawyer opens a decision record)

1. Browser: lawyer signs in and clicks a record. The web app calls GET /records/{id}.
2. API: checks the lawyer's permission for that record. If denied, it logs the attempt and returns 403.
3. API to database: writes an access-log entry (who, which record, when).
4. API to database and storage: reads the sealed record and the resume hash.
5. API: re-checks the seal and returns the record plus its verification status.
6. Browser: shows the record, the vendor explanation verbatim, and the seal status.
