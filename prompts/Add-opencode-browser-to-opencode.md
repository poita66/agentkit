# Session: Add opencode-browser to opencode

**Session ID:** ses_16a93a840ffeNF4busu5wPeQSt

**Agent:** build

**Model:** llama/default

**Messages:** 10

---

## User (1)

Add https://github.com/different-ai/opencode-browser to opencode

---

## Assistant (2)

Let me first look at the repo and your current opencode configuration.

---

## Assistant (3)

Let me check your current opencode configuration.

---

## Assistant (4)

Let me check the npm package name and then install it.

---

## Assistant (5)

Now I'll install the package and configure it.

---

## Assistant (6)

Now add the plugin to your global opencode config:

---

## Assistant (7)

Done. I've set up the `opencode-browser` plugin:

1. **Installed** `opencode-chrome-devtools` in `.opencode/package.json`
2. **Registered** the plugin in your global `~/.config/opencode/opencode.json`
3. **Added** the `browser-automation` skill to `.opencode/skill/browser-automation/SKILL.md`

To use it, start Chrome with remote debugging:
```
google-chrome --remote-debugging-port=9222
```
Then you can use tools like `browser_list`, `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_fill`, `browser_eval`, and `browser_screenshot` with `browser_url: "http://127.0.0.1:9222"`.

---

## User (8)

Will it be able to spawn a chrome instance itself? If so add directive to do so (unless an existing process is running)

---

## Assistant (9)

The plugin cannot spawn Chrome itself — it only connects to an existing CDP endpoint. I'll update the skill to instruct the agent to spawn Chrome via Bash when needed.

---

## Assistant (10)

Done. The skill now instructs the agent to:

1. Check if Chrome is already running with `curl -s http://127.0.0.1:9222/json/version`
2. If not, spawn it via Bash: `google-chrome --remote-debugging-port=9222 --no-first-run --no-default-browser-check &`
3. Fall back to `chromium` or `chromium-browser` if needed

---

