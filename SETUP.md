# One-time setup

## 1. Test the sandbox first

Open **Actions → Luna Daily Agent → Run workflow**.

It will run without any API key and create:

- reports/day-01.md
- logs/agent_events.jsonl
- an updated state.json

## 2. Give Luna a model brain

In the repository:

**Settings → Secrets and variables → Actions**

Create a repository secret:

OPENAI_API_KEY

Optionally create a repository variable:

OPENAI_MODEL

Start with the model available to your account that you explicitly choose.

Do not put the API key into any file in this repository.

## 3. Stop it

Create a file called:

KILL_SWITCH

and push it.

The next run will stop.

## 4. Remove the kill switch

Delete KILL_SWITCH and the next scheduled run can resume while mission.json remains active.

## Important

This first version is **paper mode only**. It is designed to learn the mechanics of autonomous planning and persistent state before any real-world financial permissions are considered.
