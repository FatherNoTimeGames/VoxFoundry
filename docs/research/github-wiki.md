# GitHub Wiki integration feasibility

Current official wiki docs (REFERENCES G1–G2) and a specific wiki remote have **not**
been accessed in this revised Phase 0; automatic permission review prevented the
read commands. Earlier read-only access to this code repository does not prove wiki
Git access, GitHub API scope, write rights or a wiki's existence. No wiki was created,
cloned or pushed. Do not request a token merely because GH_TOKEN is absent.

Candidate workflow to validate against official documentation: GitHub wiki content is
handled through its documented wiki Git transport, commonly a separate `.wiki.git`
remote; do not invent a REST page-write API. Availability, initialization requirements,
private-repository plan limits and accepted credential scopes need current verification.
Test the intended read-only operation with existing proxy auth first. If insufficient,
request the minimum supported secure binding; never ask for credentials in chat.

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
