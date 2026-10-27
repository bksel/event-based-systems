# Working with an AI assistant in VS Code

Optional. Nobody has to use an AI assistant for this project, and the repo works the same
without one. This page is for those who want to, using free tools. Do [SETUP.md](SETUP.md)
first.

## 1. Pick a tool

| Tool | Cost | Setup | Notes |
|---|---|---|---|
| **GitHub Copilot** (recommended) | Free for verified students via GitHub Education, otherwise a Free plan with monthly caps | Easiest | Built into VS Code, has an agent mode |
| **Gemini Code Assist** | Free individual tier | Easy | Better for questions and small edits than for long agent tasks |
| **Cline / Roo Code / Continue** | Extension is free, you supply a model | More work | Use a free API tier (Gemini, OpenRouter free models) or a local model through Ollama |

Limits and plans change often, so check the current terms.

### GitHub Copilot, step by step

1. Get the student benefit: <https://education.github.com/pack> (needs a university e-mail or
   proof of enrolment, approval can take a few days). Skip this if you are happy with the Free plan.
2. In VS Code, open *Extensions* and install **GitHub Copilot** (it includes Copilot Chat).
3. Sign in with your GitHub account when asked (account icon, bottom left).
4. Open the Chat panel and choose a mode in the dropdown:
   - **Ask**: questions about the code and the docs. Changes nothing.
   - **Edit**: you pick the files, it proposes changes to them.
   - **Agent**: it reads the repo, edits several files and runs terminal commands (asking you first).

## 2. Give it the project context

An assistant knows nothing about our project unless you show it. Attach the relevant files
to the chat (the paperclip, or type `#file`). Good starting points:

- [CONTRIBUTING.md](CONTRIBUTING.md): how we work
- [docs/domain/events.md](docs/domain/events.md) and [docs/domain/state.md](docs/domain/state.md): names of events and states
- [docs/requirements/properties.md](docs/requirements/properties.md): the safety and recoverability properties (`S1`, `L1`, ...)
- the ADR relevant to your task, from [docs/decisions/](docs/decisions/README.md)

A prompt that works:

> Read CONTRIBUTING.md and docs/domain/events.md. I'm working on task T4. Add a test for
> requirement S2 in tests/. Use the event names from the catalogue exactly. Run `just check`
> when done and show me the output.

## 3. Rules for this repo

The assistant must follow the same rules as everyone else ([CONTRIBUTING.md](CONTRIBUTING.md)).
In particular:

- **You are responsible for what you commit.** Read every diff before accepting it. "The AI
  wrote it" is not an excuse in review.
- **Run `just check`** before pushing. Do not accept a change that makes it fail.
- **Don't let it invent project facts.** Event and state names come from the
  [event catalogue](docs/domain/events.md). Requirements and open questions are referred to by
  ID. If it uses a name that is not in the catalogue, add the event there first or fix the name.
- **Don't let it decide for the team.** Design decisions go through an ADR (`just adr "Title"`),
  not through a chat answer. Don't edit accepted ADRs.
- **Dependencies only through `uv add`.** Reject manual edits to `pyproject.toml` or `uv.lock`.
- **Never commit secrets** (API keys for the tools above). Keep them in your editor settings
  or environment, not in the repo.
- **Raw sources** (PDFs, papers) stay in `docs/inbox/` and are not tracked. Pasting a
  copyrighted paper into a chat is your call, but the summary you commit
  (`just source "Title"`) must be in your own words.
- **Reports**: the text of the milestone reports is ours. Check your course's policy on AI use
  before using an assistant to write any of it, and cite it if required.

## 4. Habits that make it work better

- Work in small steps: one task or one function per request.
- Work on your own branch (`<initials>/<topic>`). If the agent makes a mess, discard the
  branch or run `git restore .`.
- Let agent mode run `just check` and read the output yourself rather than trusting its summary.
- Verify claims about Petri nets, theory or papers against the sources. Assistants state wrong
  things confidently.
- On Windows the terminal is PowerShell. If the agent suggests `bash` commands, ask it for the
  PowerShell version.
- If an answer drifts, start a new chat and re-attach the context files.
