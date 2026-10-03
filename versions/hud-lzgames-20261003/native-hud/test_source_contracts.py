"""Focused source-contract checks. These do NOT replace C++ or device tests.

Uses the actual proposed source and the exact upstream tree, never a fake emulator.
The allocation tests compile the same pure C++ helper used by the native view.
"""
from pathlib import Path
import re
import subprocess
import unittest

from apply_patch import ROOT, planned_changes
from test_patch_guards import UPSTREAM


def masked_cpp(text):
    """Blank comments and strings while preserving positions and brace structure."""
    token = re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
    return token.sub(lambda match: " " * len(match[0]), text)


def body(text, signature):
    start = text.index(signature)
    masked = masked_cpp(text)
    search_start = start + len(signature)
    if signature.endswith("("):
        # Skip default arguments such as ViewInputEventParams = {}.
        parentheses = 1
        while parentheses:
            parentheses += (masked[search_start] == "(") - (masked[search_start] == ")")
            search_start += 1
    opening = masked.index("{", search_start)
    depth = 1
    for index in range(opening + 1, len(masked)):
        depth += (masked[index] == "{") - (masked[index] == "}")
        if depth == 0:
            return text[opening + 1:index]
    raise AssertionError(f"Unbalanced source body for {signature}")


class SourceContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hud = (ROOT / "EmuFramework/src/gui/StationHudView.cc").read_text("utf-8")
        cls.changes = planned_changes(UPSTREAM)
        cls.app = cls.changes["EmuFramework/src/EmuApp.cc"].decode("utf-8")
        cls.inputs = cls.changes["EmuFramework/src/EmuInput.cc"].decode("utf-8")

    def test_both_semantic_menu_dispatchers_and_exit_use_hud(self):
        for method in ("showLastViewFromSystem", "showSystemActionsViewFromSystem", "showExitAlert"):
            code = body(self.app, f"void EmuApp::{method}(")
            self.assertIn("if(system().hasContent())", code)
            self.assertIn("showStationHud(*this, attach, e);", code)
        self.assertIn("app.showLastViewFromSystem(app.attachParams(), srcEvent);", self.inputs)
        self.assertIn("app.showSystemActionsViewFromSystem(app.attachParams(), srcEvent);", self.inputs)
        exit_action = body(self.inputs, "case exitApp:")
        self.assertIn("app.showExitAlert(app.attachParams(), srcEvent);", exit_action)

    def test_shared_show_ui_is_not_intercepted_or_reimplemented(self):
        old = (UPSTREAM / "EmuFramework/src/EmuApp.cc").read_text("utf-8")
        self.assertEqual(body(old, "void EmuApp::showUI("), body(self.app, "void EmuApp::showUI("))
        self.assertNotIn("showStationHud", body(self.app, "void EmuApp::showUI("))

    def test_modal_calls_original_engine_pause_path(self):
        bridge = body(self.hud, "void showStationHud(")
        self.assertIn("pushAndShowModal(std::make_unique<StationHudView>(attach), event, false)", bridge)
        controller = (UPSTREAM / "EmuFramework/src/gui/EmuViewController.cc").read_text("utf-8")
        self.assertIn("app().showUI(false);", body(controller, "void EmuViewController::pushAndShow("))
        self.assertIn("pauseEmulation();", body(self.app, "void EmuApp::showUI("))

    def test_state_callbacks_use_captured_engine_slots_not_selected_rows(self):
        slots = body(self.hud, "class HudSlots final")
        self.assertIn("for(int slot = 0; slot < 10; ++slot)", slots)
        self.assertIn("[this, slot](const Input::Event& e) { selectSlot(slot, e); }", slots)
        self.assertIn("entry.id = slot;", slots)
        self.assertIn("if(slot < 0 || slot >= 10) return;", body(self.hud, "void selectSlot("))
        self.assertNotIn("highlightedCell", slots)
        self.assertNotIn("selected", masked_cpp(body(self.hud, "void perform(")))
        self.assertIn('std::format("Posição {}", slot + 1)', slots)

    def test_uses_native_state_paths_and_never_automatic_slot_minus_one(self):
        perform = body(self.hud, "void perform(")
        self.assertIn("application->saveStateWithSlot(slot, true)", perform)
        self.assertIn("application->loadStateWithSlot(slot)", perform)
        self.assertIn("system().statePath(slot)", self.hud)
        for call in ("saveStateWithSlot", "loadStateWithSlot", "statePath", "setStateSlot"):
            self.assertNotRegex(masked_cpp(self.hud), rf"{call}\s*\(\s*-\s*1")
        self.assertNotIn("autosaveManager.save", masked_cpp(self.hud))
        self.assertNotIn("statePath(-1)", self.hud)

    def test_slot_change_and_resume_happen_only_after_success(self):
        perform = body(self.hud, "void perform(")
        ordered = ["bool success", "if(!success) return;", "setStateSlot(slot);", "popModalViews();", "showEmulation();"]
        offsets = [perform.index(part) for part in ordered]
        self.assertEqual(offsets, sorted(offsets))

    def test_empty_load_is_disabled_and_guarded_at_execution(self):
        self.assertIn("entries[slot]->setActive(action == StateAction::Save || exists);", self.hud)
        self.assertIn("if(entry.active()) entry.inputEvent", self.hud)
        select = body(self.hud, "void selectSlot(")
        self.assertIn("if(action == StateAction::Load && !exists)", select)
        self.assertIn("bool exists = system().stateExists(slot);", select)
        self.assertLess(select.index("if(action == StateAction::Load && !exists)"), select.index("makeView<HudConfirm>"))

    def test_overwrite_and_load_require_confirmation_of_exact_slot(self):
        select = body(self.hud, "void selectSlot(")
        bypass = body(select, "if(action == StateAction::Save && !exists)")
        self.assertIn("perform(slot);", bypass)
        self.assertIn("[this, slot] { perform(slot); }", select)
        self.assertIn('"Substituir estado" : "Carregar estado"', select)
        confirm = body(self.hud, "class HudConfirm final")
        self.assertLess(confirm.index('add("Cancelar"'), confirm.index("add(confirmLabel"))

    def test_resume_has_no_access_to_destroyed_view_after_pop(self):
        for signature in ("void resumeGame(", "void perform("):
            code = body(self.hud, signature)
            tail = code.split("application->popModalViews();", 1)[1]
            self.assertEqual(tail.strip(), "application->showEmulation();")
            self.assertIn("auto* application = &app();", code)
        settings = self.hud.split('add("Configurações"', 1)[1].split('add("Sair do jogo"', 1)[0]
        tail = settings.split("application->popModalViews();", 1)[1]
        self.assertNotIn("this", masked_cpp(tail))
        self.assertNotIn("app()", masked_cpp(tail))
        self.assertIn("application->popMenuToRoot();", tail)
        self.assertIn("application->showUI();", tail)

    def test_back_is_consumed_and_never_directly_exits(self):
        page = body(self.hud, "class HudPage :")
        cancel = body(page, "bool inputEvent(")
        self.assertIn("key->pushed(Input::DefaultKey::CANCEL)", cancel)
        self.assertIn("if(!key->repeated())", cancel)
        self.assertIn("if(cancelResumes) resumeGame();", cancel)
        self.assertIn("else dismiss();", cancel)
        self.assertNotIn("exit()", cancel)
        self.assertIn("return true;", cancel)

    def test_exit_uses_original_exiting_state_and_save_lifecycle(self):
        self.assertIn("[application] { application->appContext().exit(); }", self.hud)
        android = (UPSTREAM / "imagine/src/base/android/Application.cc").read_text("utf-8")
        exit_body = body(android, "void ApplicationContext::exit(")
        self.assertLess(exit_body.index("setExitingActivityState"), exit_body.index("jFinish(env, baseActivity)"))
        self.assertIn("app.dispatchOnExit(ctx, app.isPaused());", android)
        self.assertIn("closeSystem();", self.app)
        system = (UPSTREAM / "EmuFramework/src/EmuSystem.cc").read_text("utf-8")
        close = body(system, "void EmuSystem::closeRuntimeSystem(")
        for call in ("app.autosaveManager.save();", "app.saveSessionOptions();", "flushBackupMemory(app);"):
            self.assertIn(call, close)

    def test_no_synthetic_input_java_overlay_polling_or_process_kill(self):
        code = masked_cpp(self.hud)
        forbidden = ("dispatchTouchEvent", "dispatchKeyEvent", "Instrumentation", "sendKeyDownUpSync",
            "sendPointerSync", "AInputQueue_enqueue", "killProcess", "std::exit", "finish(",
            "std::system(", "popen(", "exec(", "addOnFrame", "setInterval", "sleep(", "usleep(")
        for api in forbidden:
            self.assertNotIn(api, code)
        self.assertIn("return menu.inputEvent(e);", code)

    def test_local_fonts_are_owned_before_children_without_changing_global_options(self):
        page = body(self.hud, "class HudPage :")
        self.assertLess(page.index("ViewManager hudManager;"), page.index("HudTable menu;"))
        self.assertLess(page.index("ViewManager hudManager;"), page.index("std::vector<std::unique_ptr<HudItem>>"))
        self.assertIn("hudManager{makeHudManager(attach)}, menu{hudAttachParams()", page)
        self.assertIn("hudManager.defaultFace.setFontSettings", page)
        self.assertIn("hudManager.defaultBoldFace.setFontSettings", page)
        self.assertNotIn("viewManager.defaultFace.setFontSettings", self.hud)
        self.assertNotIn("viewManager.defaultBoldFace.setFontSettings", self.hud)
        self.assertNotIn("fontSize =", self.hud)

    def test_full_text_is_measured_and_native_rows_follow_real_content_height(self):
        self.assertNotIn(".maxLines", self.hud)
        self.assertIn("note.fullHeight() + n", self.hud)
        self.assertIn("t.fullHeight() + detail.fullHeight()", self.hud)
        self.assertIn("menu.measuredRowHeight(inner)", self.hud)
        self.assertIn("menu.maximumRowHeight = layout.menuHeight;", self.hud)
        self.assertIn("stationHudLayout(viewRect().xSize(), viewRect().ySize()", self.hud)
        self.assertIn("t.drawScaled(cmds, {a.rect.x + a.xIndent, a.rect.y", self.hud)

    def test_original_text_api_resets_modelview_and_new_scaled_api_owns_transform(self):
        upstream = (UPSTREAM / "imagine/src/gfx/common/GfxText.cc").read_text("utf-8")
        self.assertIn("setModelView(cmds, Mat4::makeTranslate({pos.x, pos.y, 0}));", upstream)
        fixed = self.changes["imagine/src/gfx/common/GfxText.cc"].decode("utf-8")
        original_api = body(fixed, "void Text::draw(RendererCommands &cmds, WPt pos, _2DOrigin o) const")
        self.assertEqual(original_api.strip(), "drawScaled(cmds, pos, o, 1.f);")
        scaled = body(fixed, "void Text::drawScaled(RendererCommands &cmds, WPt pos, _2DOrigin o, float scale) const")
        self.assertIn("Mat4::makeTranslate({pos.x, pos.y, 0}).scale(scale)", scaled)
        self.assertIn("o.adjustX(pos.x, scaledWidth, LT2DO)", scaled)
        self.assertIn("pos.y -= scaledHeight", scaled)

    def test_all_hud_text_positions_are_absolute_and_scaled_explicitly(self):
        for field in ("t", "detail", "brand", "heading", "note"):
            self.assertIn(field + ".drawScaled(", self.hud)
            self.assertNotRegex(self.hud, rf"\b{field}\.draw\(")
            self.assertNotRegex(self.hud, rf"\b{field}\.drawScaled\(cmds,\s*\{{0,")
        self.assertIn("headingRect.x, headingRect.y", self.hud)
        self.assertIn("noteRect.x, noteRect.y", self.hud)
        self.assertIn("a.rect.x + a.xIndent, a.rect.y", self.hud)
        self.assertIn("renderer().makeClipRect(window(), headingRect)", self.hud)
        self.assertIn("renderer().makeClipRect(window(), noteRect)", self.hud)

    def test_main_hud_tries_all_five_actions_before_accepting_font_size(self):
        self.assertIn("const int requiredVisibleRows = std::min(5, int(entries.size()));", self.hud)
        self.assertIn("layout.menuHeight >= row * requiredVisibleRows", self.hud)
        self.assertIn("|| pixels == 16", self.hud)

    def test_actual_cpp_layout_helper_across_576_cases(self):
        result = subprocess.run([r"C:\Program Files\LLVM\bin\clang.exe", "-x", "c++", "-std=c++17",
            "-fsyntax-only", str(ROOT / "test_hud_layout.cpp")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
