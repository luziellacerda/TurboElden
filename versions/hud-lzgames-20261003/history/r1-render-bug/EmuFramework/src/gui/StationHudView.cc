/* TurboStations native pause HUD.
 * SPDX-License-Identifier: GPL-3.0-or-later
 * Uses the original Imagine renderer, input routing and emulator state APIs.
 * No synthetic input, Activity overlay, frame polling or independent render loop.
 */
#include <emuframework/StationHudView.hh>
#include <emuframework/EmuApp.hh>
#include <emuframework/EmuAppHelper.hh>
#include <emuframework/EmuViewController.hh>
#include <emuframework/StationHudLayout.hh>
import imagine;

namespace EmuEx
{
namespace
{
using namespace IG;
using namespace IG::Gfx;

constexpr Color green{.20f, .96f, .38f, 1.f};
constexpr Color red{1.f, .27f, .32f, 1.f};
constexpr Color white{.95f, .98f, .96f, 1.f};
constexpr Color muted{.62f, .71f, .66f, 1.f};

ViewManager makeHudManager(ViewAttachParams attach)
{
    auto& application = attach.appContext().applicationAs<EmuApp>();
    auto settings = attach.viewManager.defaultFace.fontSettings();
    ViewManager result;
    result.defaultFace = {attach.renderer(), application.fontManager.makeSystem(), settings};
    result.defaultBoldFace = {attach.renderer(), application.fontManager.makeBoldSystem(), settings};
    return result;
}

// All coordinates below are native view layout, shared by drawing and the
// original TableView hit testing. No coordinates are used to operate the emulator.
void fillRect(RendererCommands& cmds, const IQuads& unit, WRect r, Color color)
{
    cmds.basicEffect().disableTexture(cmds);
    cmds.basicEffect().setModelView(cmds, Mat4::makeTranslateScale(r));
    cmds.set(BlendMode::ALPHA);
    cmds.setColor(color);
    cmds.drawQuad(unit, 0);
    cmds.basicEffect().setModelView(cmds, Mat4::ident());
}

class HudItem final : public TextMenuItem
{
public:
    Text detail;
    bool destructive{};
    float renderScale{1.f};

    HudItem(std::string_view title, std::string_view subtitle, ViewAttachParams attach,
        SelectDelegate callback, bool danger = false):
        TextMenuItem{title, attach, callback, {.face = &attach.viewManager.defaultBoldFace}},
        detail{attach.rendererTask, subtitle, &attach.viewManager.defaultFace},
        destructive{danger} {}

    void place() final { TextMenuItem::place(); detail.compile(); }
    void prepareDraw() final { TextMenuItem::prepareDraw(); detail.makeGlyphs(); }
    int fit(int width)
    {
        // Never truncate the action or its explanation on narrow screens.
        t.compile({.maxLineSize = width});
        detail.compile({.maxLineSize = width});
        return t.fullHeight() + detail.fullHeight() + t.face()->nominalHeight();
    }
    void setDetail(std::string_view s) { detail.resetString(s); }

    void draw(RendererCommands& cmds, MenuItemDrawAttrs a) const final
    {
        auto primary = active() ? (destructive ? red : white) : muted;
        auto secondary = active() ? muted : Color{.39f, .44f, .41f, 1.f};
        int n = t.face()->nominalHeight();
        cmds.basicEffect().setModelView(cmds,
            Mat4::makeTranslate(WPt{a.rect.x + a.xIndent, a.rect.y}).scale(renderScale));
        cmds.basicEffect().enableAlphaTexture(cmds);
        t.draw(cmds, {0, n / 4}, LT2DO, primary);
        detail.draw(cmds, {0, t.fullHeight() + n / 2}, LT2DO, secondary);
        cmds.basicEffect().setModelView(cmds, Mat4::ident());
    }
};

class HudTable final : public TableView
{
    IQuads unit;
public:
    int maximumRowHeight{};
    HudTable(ViewAttachParams attach, ItemSourceDelegate source):
        TableView{attach, source}, unit{attach.rendererTask, {.size = 1}}
    {
        unit.write(0, {.bounds = WRect{{0, 0}, {1, 1}}.as<int16_t>()});
        setScrollableIfNeeded(true);
    }

    int measuredRowHeight(int width)
    {
        int n = manager().defaultFace.nominalHeight();
        int desired = std::max(1, n * 3);
        for(size_t i = 0; i < cells(); ++i)
            desired = std::max(desired, static_cast<HudItem&>(item(i)).fit(std::max(1, width - n * 2)));
        return desired;
    }

    void place() final
    {
        TableView::place();
        int desired = measuredRowHeight(viewRect().xSize());
        int row = maximumRowHeight > 0 ? std::min(desired, maximumRowHeight) : desired;
        setYCellSize(std::max(1, row));
        visibleCells = divRoundUp(std::max(1, viewRect().ySize()), yCellSize) + 1;
        for(size_t i = 0; i < cells(); ++i)
            static_cast<HudItem&>(item(i)).renderScale = float(row) / desired;
        scrollToFocusRect();
    }

    // Own drawing removes the upstream cyan table selection. Input, focus,
    // gamepad navigation and scrolling continue to use upstream TableView.
    void draw(RendererCommands& cmds, ViewDrawParams = {}) const final
    {
        if(!cells()) return;
        cmds.setClipRect(renderer().makeClipRect(window(), viewRect()));
        cmds.setClipTest(true);
        int first = std::max(0, scrollOffset() / yCellSize);
        int last = std::min(int(cells()), first + visibleCells + 1);
        int n = manager().defaultFace.nominalHeight();
        for(int i = first; i < last; ++i)
        {
            int y = viewRect().y + i * yCellSize - scrollOffset();
            WRect row{{viewRect().x, y}, {viewRect().x2, y + std::max(1, yCellSize - 3)}};
            bool focus = i == highlightedCell();
            const auto& entry = static_cast<const HudItem&>(item(i));
            fillRect(cmds, unit, row, focus ? Color{.045f, .19f, .09f, 1.f}
                                         : Color{.026f, .052f, .037f, 1.f});
            fillRect(cmds, unit, {{row.x, row.y}, {row.x + (focus ? 4 : 2), row.y2}},
                entry.destructive ? red : (focus ? green : Color{.10f, .29f, .16f, 1.f}));
            entry.draw(cmds, {.rect = row, .xIndent = n, .color = white, .align = LC2DO});
        }
        ScrollView::drawScrollContent(cmds);
        cmds.basicEffect().setModelView(cmds, Mat4::ident());
        cmds.setClipTest(false);
    }
};

class HudPage : public View, public EmuAppHelper
{
protected:
    // Constructed first/destroyed last so every child text retains a valid face.
    ViewManager hudManager;
    std::vector<std::unique_ptr<HudItem>> entries;
    // Imagine's container adapter dereferences raw pointers, not unique_ptr.
    // Separate ownership from the MenuItem pointer source just like upstream.
    std::vector<MenuItem*> itemPointers;
    HudTable menu;
    Text brand, heading, note;
    IQuads unit;
    WRect panel, headingRect, noteRect;
    StationHudLayout layout;
    int preferredFontPixels{}, measuredHeaderHeight{}, measuredFooterHeight{};
    bool cancelResumes{};

    ViewAttachParams hudAttachParams()
    {
        return {hudManager, window(), rendererTask()};
    }

    HudPage(ViewAttachParams attach, std::string_view title, std::string_view hint,
        bool resumeOnCancel = false):
        View{attach}, hudManager{makeHudManager(attach)}, menu{hudAttachParams(), itemPointers},
        brand{attach.rendererTask, "LZ GAMES  /  TURBORAMA", &hudManager.defaultBoldFace},
        heading{attach.rendererTask, title, &hudManager.defaultFace},
        note{attach.rendererTask, hint, &hudManager.defaultFace},
        unit{attach.rendererTask, {.size = 1}}, cancelResumes{resumeOnCancel}
    {
        // Fonts were fully constructed before menu/children. Emulator preferences
        // and the original ViewManager/defaultFace remain intact.
        preferredFontPixels = std::max(16, attach.viewManager.defaultFace.fontSettings().pixelHeight());
        unit.write(0, {.bounds = WRect{{0, 0}, {1, 1}}.as<int16_t>()});
        menu.setOnSelectElement([this](const Input::Event& e, int, MenuItem& entry)
        {
            if(entry.active()) entry.inputEvent(e, {.parentPtr = this});
        });
    }

    HudItem& add(std::string_view title, std::string_view hint,
        TextMenuItem::SelectDelegate callback, bool danger = false)
    {
        entries.emplace_back(std::make_unique<HudItem>(title, hint, hudAttachParams(), callback, danger));
        itemPointers.emplace_back(entries.back().get());
        return *entries.back();
    }

    void resumeGame()
    {
        // popModalViews destroys this object: do not read members afterwards.
        auto* application = &app();
        application->popModalViews();
        application->showEmulation();
    }

public:
    void place() override
    {
        // Re-measure after every local-font adjustment. Upstream's Font minimum
        // is 16 pixels; smaller windows use bounded drawing scale as a fallback.
        for(int pixels = preferredFontPixels;; pixels = std::max(16, pixels - 2))
        {
            hudManager.defaultFace.setFontSettings(renderer(), Data::FontSettings{pixels});
            hudManager.defaultBoldFace.setFontSettings(renderer(), Data::FontSettings{pixels});
            int n = std::max(1, hudManager.defaultFace.nominalHeight());
            auto preliminary = stationHudLayout(viewRect().xSize(), viewRect().ySize(), n, 0, 0, 1, 1);
            int inner = preliminary.contentWidth;
            brand.compile({.maxLineSize = inner});
            heading.compile({.maxLineSize = inner});
            note.compile({.maxLineSize = inner});
            measuredHeaderHeight = brand.fullHeight() + heading.fullHeight() + n;
            measuredFooterHeight = note.fullHeight() + n;
            int row = menu.measuredRowHeight(inner);
            layout = stationHudLayout(viewRect().xSize(), viewRect().ySize(), n,
                measuredHeaderHeight, measuredFooterHeight, row, int(entries.size()));
            if((layout.headerScale >= 1.f && layout.footerScale >= 1.f && layout.menuHeight >= row)
                || pixels == 16)
                break;
        }
        panel.setPosRel(viewRect().pos(C2DO), {layout.width, layout.height}, C2DO);
        headingRect = {{panel.x + layout.inset, panel.y},
            {panel.x2 - layout.inset, panel.y + layout.headerHeight}};
        noteRect = {{panel.x + layout.inset, panel.y2 - layout.footerHeight},
            {panel.x2 - layout.inset, panel.y2}};
        menu.maximumRowHeight = layout.menuHeight;
        menu.setViewRect({{panel.x + layout.inset, headingRect.y2},
            {panel.x2 - layout.inset, headingRect.y2 + layout.menuHeight}});
        menu.place();
    }

    void prepareDraw() override
    {
        brand.makeGlyphs(); heading.makeGlyphs(); note.makeGlyphs(); menu.prepareDraw();
    }

    void draw(RendererCommands& cmds, ViewDrawParams = {}) const override
    {
        fillRect(cmds, unit, viewRect(), {.006f, .012f, .009f, .86f});
        fillRect(cmds, unit, panel, {.015f, .03f, .021f, .98f});
        fillRect(cmds, unit, {{panel.x, panel.y}, {panel.x2, std::min(panel.y2, panel.y + 3)}}, green);
        fillRect(cmds, unit, {{std::max(panel.x, panel.x2 - 40), panel.y},
            {panel.x2, std::min(panel.y2, panel.y + 3)}}, red);
        cmds.basicEffect().enableAlphaTexture(cmds);
        int n = hudManager.defaultFace.nominalHeight();
        if(layout.headerHeight > 0)
        {
            cmds.basicEffect().setModelView(cmds,
                Mat4::makeTranslate(WPt{headingRect.x, headingRect.y}).scale(layout.headerScale));
            brand.draw(cmds, {0, n / 3}, LT2DO, green);
            heading.draw(cmds, {0, brand.fullHeight() + n / 2}, LT2DO, white);
        }
        if(layout.footerHeight > 0)
        {
            cmds.basicEffect().setModelView(cmds,
                Mat4::makeTranslate(WPt{noteRect.x, noteRect.y}).scale(layout.footerScale));
            note.draw(cmds, {0, n / 2}, LT2DO, muted);
        }
        cmds.basicEffect().setModelView(cmds, Mat4::ident());
        menu.draw(cmds);
    }

    void onAddedToController(ViewController* c, const Input::Event& e) override
    {
        menu.setController(c, e);
        menu.highlightCell(0);
    }
    void onShow() override { menu.onShow(); place(); postDraw(); }
    void onHide() override { menu.onHide(); }
    void setFocus(bool focused) override { menu.setFocus(focused); }
    bool inputEvent(const Input::Event& e, ViewInputEventParams = {}) override
    {
        if(auto* key = e.keyEvent(); key && key->pushed(Input::DefaultKey::CANCEL))
        {
            if(!key->repeated())
            {
                if(cancelResumes) resumeGame();
                else dismiss();
            }
            return true;
        }
        return menu.inputEvent(e);
    }
};

class HudConfirm final : public HudPage
{
public:
    HudConfirm(ViewAttachParams attach, std::string_view title, std::string_view message,
        std::string_view confirmLabel, TextMenuItem::SelectDelegate action, bool danger = false):
        HudPage{attach, title, message}
    {
        // Safe default for physical controllers: cancellation is first/focused.
        add("Cancelar", "Voltar sem executar esta ação.", [this] { dismiss(); });
        add(confirmLabel, "Confirmar a ação descrita acima.", action, danger);
    }
};

enum class StateAction { Save, Load };

class HudSlots final : public HudPage
{
    StateAction action;

    void perform(int slot)
    {
        auto* application = &app();
        bool success = action == StateAction::Save
            ? application->saveStateWithSlot(slot, true)
            : application->loadStateWithSlot(slot);
        if(!success) return; // Keep the native error message and the paused menu.
        application->setStateSlot(slot);
        application->popModalViews();
        application->showEmulation();
    }

    void selectSlot(int slot, const Input::Event& e)
    {
        // A captured engine slot (0..9), never a UI row or highlighted index.
        if(slot < 0 || slot >= 10) return;
        bool exists = system().stateExists(slot);
        if(action == StateAction::Load && !exists)
        {
            app().postMessage("Esta posição ainda não contém um estado salvo.");
            return;
        }
        if(action == StateAction::Save && !exists)
        {
            perform(slot);
            return;
        }
        auto title = std::format("{} estado — posição {}", action == StateAction::Save ? "Substituir" : "Carregar", slot + 1);
        auto message = action == StateAction::Save
            ? "O estado desta posição será substituído pelo momento atual. Outras posições não serão alteradas."
            : "O jogo voltará ao momento salvo nesta posição. O progresso atual que não foi salvo será perdido.";
        pushAndShowModal(makeView<HudConfirm>(title, message,
            action == StateAction::Save ? "Substituir estado" : "Carregar estado",
            [this, slot] { perform(slot); }), e);
    }

public:
    HudSlots(ViewAttachParams attach, StateAction requested):
        HudPage{attach, requested == StateAction::Save ? "SALVAR ESTADO" : "CARREGAR ESTADO",
            "Escolha uma das 10 posições. Voltar cancela sem alterar o jogo."},
        action{requested}
    {
        for(int slot = 0; slot < 10; ++slot)
        {
            auto label = std::format("Posição {}", slot + 1);
            auto& entry = add(label, "", [this, slot](const Input::Event& e) { selectSlot(slot, e); });
            entry.id = slot;
        }
        add("Voltar ao menu", "Escolher outra ação; o jogo continua pausado.", [this] { dismiss(); });
    }
    void onShow() final
    {
        for(int slot = 0; slot < 10; ++slot)
        {
            bool exists = system().stateExists(slot);
            auto timestamp = exists ? appContext().fileUriFormatLastWriteTimeLocal(system().statePath(slot)) : std::string{};
            entries[slot]->setDetail(exists ? std::format("Salvo: {}", timestamp)
                : (action == StateAction::Save ? "Vazia — guardar um novo estado aqui." : "Vazia — nenhum estado para carregar."));
            entries[slot]->setActive(action == StateAction::Save || exists);
        }
        HudPage::onShow();
    }
};

class StationHudView final : public HudPage
{
public:
    explicit StationHudView(ViewAttachParams attach):
        HudPage{attach, "JOGO PAUSADO", "Escolha uma ação. Voltar continua o jogo com os controles do emulador.", true}
    {
        add("Continuar jogo", "Retomar do mesmo ponto, sem alterar nada.", [this] { resumeGame(); });
        add("Salvar estado", "Escolher uma posição e guardar o momento atual.", [this](const Input::Event& e)
        { pushAndShowModal(makeView<HudSlots>(StateAction::Save), e); });
        add("Carregar estado", "Escolher uma posição salva para continuar dali.", [this](const Input::Event& e)
        { pushAndShowModal(makeView<HudSlots>(StateAction::Load), e); });
        add("Configurações", "Abrir as opções e controles originais deste emulador.", [this]
        {
            auto* application = &app();
            application->popModalViews();
            application->popMenuToRoot();
            application->showUI();
        });
        add("Sair do jogo", "Encerrar a emulação e voltar às plataformas.", [this](const Input::Event& e)
        {
            auto* application = &app();
            pushAndShowModal(makeView<HudConfirm>("VOLTAR ÀS PLATAFORMAS?",
                "O emulador executará sua rotina de gravação e encerrará o jogo. O estado automático depende das suas configurações. Para guardar um ponto manual, cancele e use Salvar estado.",
                "Sair e voltar às plataformas", [application] { application->appContext().exit(); }, true), e);
        }, true);
    }
};
}

void showStationHud(EmuApp& app, ViewAttachParams attach, const Input::Event& event)
{
    if(!app.system().hasContent()) return;
    // Upstream pushAndShowModal invokes showUI(false): engine thread is stopped,
    // audio paused and fast-forward reset before drawing this native view.
    app.viewController().pushAndShowModal(std::make_unique<StationHudView>(attach), event, false);
}
}
