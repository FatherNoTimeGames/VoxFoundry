# GitHub Wiki integration feasibility

Official wiki documentation G2 was retrieved/read on continuation. It verifies that
wiki pages may be edited locally through Git, with a separate HTTPS `.wiki.git` clone
URL after an initial page is created on GitHub. Only changes pushed to its default
branch are published. The default branch must be discovered, not assumed by name.
The documented forbidden filename characters are `\ / : * ? " < > |`, relevant to
Windows-safe page export/import.

No specific wiki remote or credential scope has been tested. Earlier code-repository
read access does not prove wiki existence/access or write permission. No wiki was
created, cloned or pushed. Do not request a token merely because GH_TOKEN is absent.
Current private-repository/plan eligibility and accepted credential scopes still need
verification from full official docs (G1) and intended read-only operations.
Use the documented Git workflow rather than inventing a REST page-write API. Test
native Git with existing proxy authentication first; if insufficient, request only
an appropriate secure binding, never secret values in chat.

## Safe bidirectional design

Import a pinned wiki revision and index source pages under stable source IDs. Store
remote revision SHA, path, digest, retrieval date and project mapping. Treat all page
content/links as untrusted; do not execute HTML/scripts or fetch arbitrary URLs while
indexing. Preserve original source and local independent backup.

External-change detection fetches new revisions and compares baseline → remote and
baseline → local proposal. Conflicts go to the central Review Queue with readable
Android-friendly diffs and provenance. AI/local drafts never edit approved canon or
push automatically. Local acceptance records a review decision; publishing is a
separate explicit approval of the exact diff and expected remote head. Re-fetch before
write, require a fast-forward/expected-base check, and surface concurrent changes.
Never force-push or silently overwrite remote edits. Failed publication retains the
approved local proposal and diagnostics. Store no tokens in Git remotes, exports or logs.

Evidence still required: public/private wiki read with intended auth, external update
conflict, safe local proposal/approval, explicitly authorized disposable wiki push,
read-after-write, revocation, malformed imports and independent backup restoration.
No publishing test is authorized by the current Phase 0 request alone; prepare the
exact disposable diff/target before seeking explicit remote-write approval.
