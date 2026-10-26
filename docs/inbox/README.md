# Inbox

Drop anything you want to read or mine for the project here: papers, lecture
slides, web articles saved as PDF/HTML/Markdown, datasheets, chat exports.

**Nothing in this folder except this README and `.gitignore` is tracked by git.**
Files here are personal and are not shared with the team. To share what you learned:

1. Run `just source "Short title"`. It creates `docs/sources/short-title.md` and adds it to the
   [sources index](../sources/README.md).
2. Fill in the summary: the citation, the key points, and how it affects *our* model or
   simulator. Link to the KB pages or ADRs it informs.
3. If the source changes a decision, write or update an ADR (`just adr "..."`).
4. Commit the summary. Delete the raw file when you no longer need it.

If a source is freely available online, put its URL in the summary so teammates can get
the original.
