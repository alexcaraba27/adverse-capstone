# 001: Stack for Adverse MVP

- **Context:** Adverse is a multi-user, tamper-evident record of AI hiring decisions that has to keep records for 4+ years and keep signing logic off the browser.
- **Decision:** Supabase (Postgres, Auth, Storage) for data and logins, FastAPI for capture, sealing, and the API, and a Next.js web app for the lawyer's record view.
- **Why not Firebase:** Firebase covers the same jobs, but Firestore isn't SQL, so moving years of legal records off it later is harder. Supabase's cost: the free tier pauses idle projects, and I'm still running my own back end (FastAPI) next to it.
- **What would change my mind:** if Supabase's append-only and Row Level Security setup can't actually stop edits to sealed records or access-log rows, or if hosting FastAPI separately is too much to manage in five weeks.
