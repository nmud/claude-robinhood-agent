# DEPLOY — run this on your phone

Goal: reach the full workflow (files, MCP, autonomous loop) from your phone, anywhere.

Best solo setup = an always-on box runs Claude Code + this repo; your phone connects to it over a private network. The box keeps the journal and runs the loop even when your phone is in your pocket.

---

## 1. Pick a box (always-on)
- **Cloud:** $5/mo VPS — Hetzner, DigitalOcean, or AWS Lightsail (US region, near markets). Easiest, reliable.
- **Home:** Raspberry Pi 5, an old laptop, or a mini-PC. Free if you have one. Leave it on.

## 2. Set up the box
```bash
# install Node + git (Debian/Ubuntu example)
sudo apt update && sudo apt install -y nodejs npm git
# install Claude Code
npm install -g @anthropic-ai/claude-code
# clone your repo
git clone https://github.com/nmud/claude-robinhood-agent.git
cd claude-robinhood-agent
# log in to Claude Code (follow the prompt)
claude
```

## 3. Wire the Robinhood MCP (on the box)
```bash
# add the remote Robinhood agentic MCP (paste the URL from robinhood.com/agentic-trading)
claude mcp add robinhood-trading <ROBINHOOD_MCP_URL>
```
- Auth happens in-session the first time. **MCP tokens stay on the box — never commit them** (`.gitignore` already blocks `mcp.json`/`.env`).

## 4. Private network — Tailscale (no exposed ports)
- Install Tailscale on the **box** and your **phone**, log into the same account.
- Box gets a private IP like `100.x.x.x`. Only your devices can reach it. No public SSH port, no firewall holes.
```bash
curl -fsSL https://tailscale.com/install.sh | sh && sudo tailscale up
tailscale ip -4   # note this IP
```

## 5. Phone → box
- Install **Termius** (iOS/Android) or **Blink** (iOS).
- New host: the box's Tailscale IP, your username, your SSH key (use keys, not passwords).
- Connect → `cd claude-robinhood-agent` → `claude`. Full workflow, on your phone.

## 6. The autonomous loop (runs 24/7 on the box)
Two ways:
- **tmux session:** `tmux new -s trader` → start `claude`, run `/loop` with your pass prompt → detach (`Ctrl-b d`). Reattach from phone anytime.
- **cron (market hours only):** trigger a one-shot analysis pass every N minutes, e.g.:
```cron
# every 15 min, 9:30-16:00 ET, Mon-Fri  (set box TZ to America/New_York)
*/15 13-20 * * 1-5  cd ~/claude-robinhood-agent && claude -p "run one analysis pass per CLAUDE.md" >> loop.log 2>&1
```
Keep `config.md` interval and this cadence in sync.

## 7. Get pinged when it trades (optional)
Have the loop send a push on order placed — free via [ntfy.sh](https://ntfy.sh) or Pushover:
```bash
curl -d "AUTO bought 0.5 SPY @ 741" ntfy.sh/your-private-topic
```
Subscribe to the topic in the ntfy phone app.

---

## Security checklist
- SSH **keys only**, password login disabled.
- Access **only** via Tailscale — no public ports open.
- MCP tokens / `.env` never committed (`.gitignore` covers it).
- Box firewall on (`ufw`), auto-updates enabled.
- Stay in **ADVISE** until you trust it; arm AUTO only after `config.md` is set.

## Lazy alternative (no box, weaker loop)
Push repo to GitHub → open **claude.ai/code** in your phone browser → connect the repo → configure the MCP there. Good for asking on the go; the cloud env is ephemeral, so the 24/7 autonomous loop won't run while it's asleep. Use the box for real autonomy.
