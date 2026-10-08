#!/usr/bin/env python3
from __future__ import annotations
import csv, datetime as dt, json, os, pathlib, urllib.request

ROOT=pathlib.Path(__file__).resolve().parent
MISSION,STATE,LEDGER=ROOT/"mission.json",ROOT/"state.json",ROOT/"ledger.csv"
REPORTS,LOGS,KILL=ROOT/"reports",ROOT/"logs",ROOT/"KILL_SWITCH"

def read_json(p):
    with p.open(encoding="utf-8") as f:return json.load(f)
def write_json(p,d):
    tmp=p.with_suffix(p.suffix+".tmp")
    with tmp.open("w",encoding="utf-8") as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write("\n")
    tmp.replace(p)
def read_ledger():
    if not LEDGER.exists():return []
    with LEDGER.open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f))
def event(d):
    LOGS.mkdir(parents=True,exist_ok=True)
    with (LOGS/"agent_events.jsonl").open("a",encoding="utf-8") as f:f.write(json.dumps(d,ensure_ascii=False)+"\n")
def call_model(prompt):
    key=os.getenv("OPENAI_API_KEY")
    if not key:return None
    payload={"model":os.getenv("OPENAI_MODEL","gpt-5.6-mini"),"input":prompt}
    req=urllib.request.Request("https://api.openai.com/v1/responses",data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=90) as r:raw=json.loads(r.read().decode())
    except Exception as exc:
        event({"timestamp":dt.datetime.now(dt.timezone.utc).isoformat(),"type":"model_error","error":str(exc)});return None
    parts=[]
    for item in raw.get("output",[]):
        for c in item.get("content",[]):
            if c.get("type") in {"output_text","text"} and c.get("text"):parts.append(c["text"])
    text="\n".join(parts).strip()
    try:return json.loads(text)
    except Exception:return {"summary":text,"experiments":[],"chosen_action":"Review model output manually.","risk":"Model did not return strict JSON."}
def fallback():
    return {"summary":"Paper-mode heartbeat. Find one narrow problem with a plausible buyer and gather evidence before claiming revenue.","experiments":[{"name":"Micro-product research","hypothesis":"A narrow template or tool can solve a painful repeat problem.","paper_cost_usd":0,"paper_revenue_usd":0,"evidence_needed":["specific problem","existing alternatives","willingness-to-pay signal"]},{"name":"Research-to-artifact service","hypothesis":"People may pay for concise, cited research artifacts.","paper_cost_usd":0,"paper_revenue_usd":0,"evidence_needed":["clear buyer","repeatability","time saved"]}],"chosen_action":"Collect evidence for one narrowly defined problem.","risk":"This is a hypothesis; no revenue is assumed."}
def main():
    mission,state,rows=read_json(MISSION),read_json(STATE),read_ledger()
    today=dt.date.today();start=dt.date.fromisoformat(mission["start_date"]);day=max(1,(today-start).days+1);now=dt.datetime.now(dt.timezone.utc).isoformat()
    if KILL.exists() or mission.get("status")=="paused":
        state["status"]="paused";state["last_run_at"]=now;write_json(STATE,state);event({"timestamp":now,"type":"paused"});return
    if day>int(mission["duration_days"]):
        state["status"]="completed";state["last_run_at"]=now;write_json(STATE,state);event({"timestamp":now,"type":"completed"});return
    prompt="You are Luna inside a 30-day paper-money agency experiment.\nMission: "+json.dumps(mission,ensure_ascii=False)+"\nState: "+json.dumps(state,ensure_ascii=False)+"\nRecent ledger: "+json.dumps(rows[-12:],ensure_ascii=False)+f"\nToday is day {day}.\nChoose the smallest useful next research/action step. Never use real money, banks, cards, financial accounts, credentials, unsolicited outreach, impersonation, or irreversible external actions. Return STRICT JSON with summary, experiments (name,hypothesis,paper_cost_usd,paper_revenue_usd,evidence_needed), chosen_action, risk. Prefer one concrete experiment over grand strategy."
    plan=call_model(prompt) or fallback()
    REPORTS.mkdir(exist_ok=True)
    report=f"# Luna Daily Report — Day {day}\n\nDate: {today.isoformat()}\nMode: **{mission['mode']}**\nPaper wallet: **{state.get('paper_wallet_usd',100):.2f} USD**\n\n## Summary\n{plan.get('summary','')}\n\n## Candidate experiments\n"
    for x in plan.get("experiments",[]):report+=f"### {x.get('name','Unnamed')}\n- Hypothesis: {x.get('hypothesis','')}\n- Paper cost: {float(x.get('paper_cost_usd',0) or 0):.2f} USD\n- Paper revenue: {float(x.get('paper_revenue_usd',0) or 0):.2f} USD\n- Evidence: {'; '.join(x.get('evidence_needed',[]))}\n\n"
    report+=f"## Chosen action\n{plan.get('chosen_action','')}\n\n## Risk / uncertainty\n{plan.get('risk','')}\n\n> Paper mode only. No real money or external account action is permitted.\n"
    (REPORTS/f"day-{day:02d}.md").write_text(report,encoding="utf-8")
    state["last_run_at"]=now;state["run_count"]=int(state.get("run_count",0))+1;state["current_focus"]=plan.get("chosen_action",state.get("current_focus"));state["notes"]=(state.get("notes",[])+[plan.get("summary","")])[-10:];write_json(STATE,state)
    event({"timestamp":now,"type":"daily_run","day":day,"model_enabled":bool(os.getenv("OPENAI_API_KEY")),"chosen_action":plan.get("chosen_action")})
if __name__=="__main__":main()
