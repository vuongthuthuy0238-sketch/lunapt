# LunaPT — 30-Day Self-Sustainability Sandbox

A small, observable agent experiment for Thủy and Luna.

## Goal

Give the agent a finite virtual runway and 30 days to search for legitimate ways to create value.

**Initial paper capital:** $100  
**Mode:** paper-money / no real financial transactions  
**Runtime:** GitHub Actions  
**Memory:** repository files  
**Human control:** KILL_SWITCH file + normal repository permissions

The first phase is intentionally conservative. The agent may research, write plans, create experiments, and update its own logs. It may not move real money, access a bank account, buy financial assets, send unsolicited messages, or publish irreversible external changes.

## How it runs

A scheduled GitHub Actions workflow runs once per day.

1. checks out this repository;
2. runs agent.py;
3. writes a daily report and event log;
4. commits the new state back to main.

## Optional model brain

Add a repository secret named OPENAI_API_KEY and optionally a repository variable named OPENAI_MODEL.

The agent calls the OpenAI Responses API over HTTPS. Without the key, it still runs a deterministic heartbeat so the sandbox can be tested safely.

## Stop the agent

Create this file:

KILL_SWITCH

or change mission.json:

"status": "paused"

The next scheduled run will stop and record the reason.

## Where things live

- mission.json — mission, limits, and safety rules
- state.json — current run state
- ledger.csv — paper financial ledger
- agent.py — agent loop
- reports/ — daily reports
- logs/ — event log
- experiments/ — artifacts
- skills/ — reusable operating rules

## Phase 2

Only after the paper sandbox is behaving well should we consider narrow real-world actions, one permission at a time, with explicit approval and a reversible path.

This is an experiment in agency, not a promise of profit.
