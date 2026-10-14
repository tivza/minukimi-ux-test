# MINUKIMI UX Research v0.7 — deploy-ready

This folder is ready for a public HTTPS test on Render.

## Recommended today: free Render Blueprint

`render.yaml` creates:

- one free Python web service;
- one free Render Postgres database for persistent research sessions;
- a generated `ADMIN_TOKEN`;
- health check at `/api/health`.

Render's free Postgres database is suitable for this short pilot but expires after 30 days. Export the data from the dashboard before then.

## After deploy

Tester URL:

`https://<your-service>.onrender.com/`

Research dashboard:

`https://<your-service>.onrender.com/dashboard.html`

The dashboard asks for `ADMIN_TOKEN`. Copy its generated value from the Render service environment variables.

Health check:

`https://<your-service>.onrender.com/api/health`

Expected JSON contains `"ok": true`, `"version": "0.7"`, and `"database": "postgres"`.

## Local verification

```bash
python server.py
```

Local mode falls back to SQLite and prints a temporary admin token.

## Paid alternative

`render-sqlite-paid.yaml` uses a paid web service with a 1 GB persistent disk and SQLite instead of Postgres.

## Test flow

1. Complete the test yourself on the public URL.
2. Open the admin dashboard and verify that your completed session appears.
3. Export CSV once as a backup.
4. Send the tester URL to 5 pilot users.
5. Review incomplete sessions, gesture abandonment, dwell time, prompt/control recall, and open answers.
