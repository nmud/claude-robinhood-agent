# SETUP — bootstrap on a new machine

For phone access / always-on box ideas see DEPLOY.md. This is the minimal path.

## 1. Install
```bash
# Node 22+, git, then:
npm install -g @anthropic-ai/claude-code
```

## 2. Repo
```bash
git clone https://github.com/nmud/claude-robinhood-agent.git
cd claude-robinhood-agent
git checkout news-framework
```

## 3. Auth (all three are per-machine — redo on every new box)
```bash
claude                      # then /login with the Max account
claude mcp add robinhood-trading --transport http https://agent.robinhood.com/mcp/trading
# inside claude: /mcp -> robinhood-trading -> authenticate (Robinhood OAuth)
# git push auth: `gh auth login`, or a PAT, or VS Code's GitHub sign-in
```

## 4. Preflight (mandatory on every new machine)
Inside claude: `Run the preflight per prompts/preflight.md`
Read findings/preflight-*.md — tool names, historical-data source, account
type, and reconciliation must all PASS before any trading mode runs here.

## 5. Schedule (system crontab — survives reboots and Claude sessions)
```cron
# times in UTC — shift by your box's timezone; 13:45 UTC = 9:45am ET (DST)
45 13 * * 1-5  /FULL/PATH/claude-robinhood-agent/scripts/daily_run.sh
47 21 * * *    /FULL/PATH/claude-robinhood-agent/scripts/iterate_run.sh
30 21 * * 5    /FULL/PATH/claude-robinhood-agent/scripts/weekly_run.sh
```
Or interactively: `/loop 15m Run one tick per prompts/tick.md`

## 6. Sanity rules for migration
- Mode in config.md stays SIM until the new box passes preflight AND one clean
  simulated day (TESTING.md has the graduation ladder).
- Never run trading crons on two machines at once — one broker, one brain.
  Disable the old box's crons before enabling the new one's.
- The journal/ledger lives in git: pull before every run, push after (the
  scripts do this). If push fails on the new box, fix git auth before AUTO.
