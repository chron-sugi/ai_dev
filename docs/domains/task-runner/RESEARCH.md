They overlap on "what runs" but differ on *when* and *how guaranteed* — they're actually complementary layers:

**Invocation model**
- **just** is opt-in: `just lint` runs ruff because someone (human or agent) chose to run it. It's a discoverable menu of canonical commands.
- **pre-commit** is event-triggered: ruff runs because a commit happened, whether or not anyone thought to run it. Nobody chooses.

That's the core difference in your terms: just is *convention* (the agent should run `just lint`), pre-commit is *mechanism* (the agent cannot commit unformatted code). An agent that forgets, skips, or never learned about `just lint` still hits the pre-commit gate. It's the same distinction as prose instructions vs. lint config, one level up.

**Other practical differences**
- **Scope**: pre-commit runs only on *staged files* by default — fast, targeted. `just lint` typically runs repo-wide. For big repos that's a real feedback-latency difference in the agent loop.
- **Tool pinning**: pre-commit manages its own hook environments with pinned versions from the config. Just runs whatever's on PATH — so `just lint` can behave differently per machine/session unless you pair it with mise. Pre-commit gives you determinism for free.
- **Escape hatch**: `git commit --no-verify` bypasses pre-commit. Worth knowing: agents occasionally learn this trick, which is an argument for your server-side or push-level backstop remaining in place.

**How they compose well**
The clean pattern is: justfile recipes are the *source of truth* for commands, and pre-commit hooks *call* the just recipes (or the same underlying commands). Agents use just during active development for fast, deliberate feedback — `just test`, `just lint` mid-loop — and pre-commit is the safety net that catches whatever the agent didn't voluntarily run. Same commands, two invocation paths: menu and gate.

So the answer to "why both": just optimizes the *happy path* (agent knows what to run, runs it early and often), pre-commit closes the *unhappy path* (agent didn't run it, gate catches it). Your enforcement-layering principle already predicts this — you want the deliberate layer for speed and the mechanical layer for guarantees.