import shutil
import time

from playwright.sync_api import expect, sync_playwright
from test_browser import running_app
from voxfoundry.application.manuscripts import Manuscripts


def test_manuscript_import_autosave_history_restore_dictionary_restart(tmp_path, monkeypatch):
    original_save = Manuscripts.save_draft

    def slow_save(self, *args, **kwargs):
        time.sleep(0.25)  # allow typing while a real backend save is in flight
        return original_save(self, *args, **kwargs)

    monkeypatch.setattr(Manuscripts, "save_draft", slow_save)
    errors = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=shutil.which("chromium"))
        page = browser.new_page(viewport={"width": 1280, "height": 1000})
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("dialog", lambda dialog: dialog.accept())
        with running_app(tmp_path / "library") as address:
            page.goto(address)
            page.get_by_label("New project name").fill("Manuscript project")
            page.get_by_role("button", name="Create project", exact=True).click()
            page.get_by_text("Add or import document", exact=True).click()
            page.get_by_label("New document title").fill("Part One")
            page.get_by_label("Document kind", exact=True).select_option("part")
            page.get_by_role("button", name="Create document", exact=True).click()
            expect(page.get_by_role("heading", name="Part One", exact=True)).to_be_visible()
            page.get_by_label("Import title").fill("Chapter One")
            page.get_by_label("Import parent").select_option(label="Part One")
            original = b"# Chapter\n\n<script>window.importedCodeExecuted=true</script>\n"
            page.get_by_label("TXT or Markdown file").set_input_files(
                {"name": "original.md", "mimeType": "text/markdown", "buffer": original}
            )
            page.get_by_role("button", name="Import manuscript", exact=True).click()
            editor = page.get_by_label("Manuscript text", exact=True)
            expect(editor).to_have_value(original.decode())
            assert page.evaluate("window.importedCodeExecuted") is None
            # Typing during an earlier autosave must persist the latest text, not overwrite it.
            with page.expect_request("**/draft"):
                editor.fill("Earlier text waiting to save.")
            editor.fill("Embervale is ancient.\n\nThe final paragraph.")
            expect(page.locator(".draft-status")).to_have_text("Draft saved locally.")
            page.get_by_label("Revision note").fill("Approved draft")
            page.get_by_role("button", name="Freeze revision", exact=True).click()
            expect(page.get_by_role("status").filter(has_text="Revision frozen.")).to_be_visible()
            page.get_by_text("Project snapshots", exact=True).click()
            page.get_by_label("Snapshot name").fill("First edition")
            page.get_by_role("button", name="Create project snapshot", exact=True).click()
            expect(
                page.get_by_role("status").filter(has_text="Project snapshot created.")
            ).to_be_visible()
            editor.fill("Later work worth preserving.")
            expect(page.locator(".draft-status")).to_have_text("Draft saved locally.")
            page.get_by_text("Revision comparison and restoration", exact=True).click()
            revision_select = page.get_by_label("Revision", exact=True)
            revision_id = (
                revision_select.locator("option")
                .filter(has_text="Approved draft")
                .get_attribute("value")
            )
            revision_select.select_option(revision_id)
            page.get_by_role("button", name="Compare revision to draft", exact=True).click()
            expect(
                page.locator(".diff").filter(has_text="Later work worth preserving")
            ).to_be_visible()
            page.get_by_role("button", name="Restore revision", exact=True).click()
            expect(editor).to_have_value("Embervale is ancient.\n\nThe final paragraph.")
            page.get_by_text("Pronunciation dictionary and presets", exact=True).click()
            page.get_by_label("Pronunciation term").fill("Embervale")
            page.get_by_label("Spoken replacement").fill("Ember-vail")
            page.get_by_role("button", name="Save pronunciation rule", exact=True).click()
            expect(
                page.get_by_role("status").filter(has_text="Pronunciation settings saved")
            ).to_be_visible()
            page.get_by_text("Pronunciation preview for frozen script", exact=True).click()
            page.get_by_role("button", name="Preview pronunciations", exact=True).click()
            expect(page.get_by_text("Ember-vail is ancient.", exact=True)).to_be_visible()
            # Snapshot restoration previews and preserves the newer settings/history.
            snapshots = page.get_by_label("Snapshot", exact=True)
            snapshot_id = (
                snapshots.locator("option").filter(has_text="First edition").get_attribute("value")
            )
            snapshots.select_option(snapshot_id)
            page.get_by_role("button", name="Preview snapshot restoration", exact=True).click()
            expect(page.get_by_role("heading", name="Changes to restore")).to_be_visible()
            page.get_by_role("button", name="Restore project snapshot", exact=True).click()
            expect(
                page.get_by_role("status").filter(
                    has_text="Project snapshot restored; later history retained."
                )
            ).to_be_visible()
            page.get_by_role("button", name="— Chapter One (manuscript)", exact=True).click()
            expect(editor).to_have_value("Embervale is ancient.\n\nThe final paragraph.")
        with running_app(tmp_path / "library") as address:
            page.set_viewport_size({"width": 390, "height": 844})
            page.goto(address)
            page.get_by_role("button", name="Manuscript project", exact=True).click()
            page.get_by_role("button", name="— Chapter One (manuscript)", exact=True).click()
            expect(editor).to_have_value("Embervale is ancient.\n\nThe final paragraph.")
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            page.get_by_text("Project snapshots", exact=True).click()
            expect(
                page.get_by_label("Snapshot", exact=True)
                .locator("option")
                .filter(has_text="Before snapshot restore")
            ).to_have_count(1)
        browser.close()
    assert errors == []


def test_two_browser_tabs_preserve_conflicted_local_text(tmp_path):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=shutil.which("chromium"))
        context = browser.new_context()
        page = context.new_page()
        with running_app(tmp_path / "library") as address:
            page.goto(address)
            page.get_by_label("New project name").fill("Conflict test")
            page.get_by_role("button", name="Create project", exact=True).click()
            page.get_by_text("Add or import document", exact=True).click()
            page.get_by_label("New document title").fill("Shared draft")
            page.get_by_role("button", name="Create document", exact=True).click()
            expect(page.get_by_label("Manuscript text", exact=True)).to_have_value("")
            other = context.new_page()
            other.goto(address.split("#")[0])
            other.get_by_role("button", name="Conflict test", exact=True).click()
            other.get_by_role("button", name="Shared draft (manuscript)", exact=True).click()
            expect(other.get_by_label("Manuscript text", exact=True)).to_have_value("")
            page.get_by_label("Manuscript text", exact=True).fill("Server version from first tab")
            expect(page.locator(".draft-status")).to_have_text("Draft saved locally.")
            other.get_by_label("Manuscript text", exact=True).fill(
                "Local text from stale second tab"
            )
            expect(
                other.get_by_role("alert").filter(has_text="Draft changed in another editor")
            ).to_be_visible()
            expect(other.get_by_label("Manuscript text", exact=True)).to_have_value(
                "Local text from stale second tab"
            )
            other.get_by_label("Manuscript text", exact=True).fill(
                "Still editing locally after conflict"
            )
            expect(other.locator(".draft-status")).to_have_text(
                "Unsaved draft — keep this page open."
            )
            page.get_by_role("button", name="Reload manuscript", exact=True).click()
            expect(page.get_by_label("Manuscript text", exact=True)).to_have_value(
                "Server version from first tab"
            )
            other.on("dialog", lambda dialog: dialog.accept())
            other.get_by_role("button", name="Reload manuscript", exact=True).click()
            expect(other.get_by_label("Manuscript text", exact=True)).to_have_value(
                "Server version from first tab"
            )

            # A real concurrent settings edit must not clear a rejected rule form.
            page.get_by_text("Pronunciation dictionary and presets", exact=True).click()
            page.get_by_label("Pronunciation term").fill("Embervale")
            page.get_by_label("Spoken replacement").fill("Local replacement")
            origin = address.split("/#")[0]
            project = other.request.get(origin + "/api/projects").json()[0]
            session = other.request.get(origin + "/api/session").json()
            changed = other.request.put(
                origin + "/api/projects/" + project["id"] + "/settings",
                data={"version": 0, "rules": [{"term": "Another", "replacement": "Rule"}]},
                headers={"Origin": origin, "X-VF-CSRF": session["csrf"]},
            )
            assert changed.status == 200
            page.get_by_role("button", name="Save pronunciation rule", exact=True).click()
            expect(page.get_by_role("alert").filter(has_text="Settings changed")).to_be_visible()
            expect(page.get_by_label("Pronunciation term")).to_have_value("Embervale")
            expect(page.get_by_label("Spoken replacement")).to_have_value("Local replacement")
        browser.close()
