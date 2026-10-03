/* Native HUD allocation, independent of graphics for direct host tests.
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
#pragma once

namespace EmuEx
{
constexpr int hudMin(int a, int b) { return a < b ? a : b; }
constexpr int hudMax(int a, int b) { return a > b ? a : b; }

struct StationHudLayout
{
    int margin{}, width{}, height{}, inset{}, contentWidth{};
    int headerHeight{}, menuHeight{}, footerHeight{};
    float headerScale{1.f}, footerScale{1.f};
};

constexpr StationHudLayout stationHudLayout(int windowWidth, int windowHeight,
    int nominal, int requestedHeader, int requestedFooter, int requestedRow, int rows)
{
    const int vw = hudMax(1, windowWidth), vh = hudMax(1, windowHeight);
    const int n = hudMax(1, nominal);
    StationHudLayout out;
    out.margin = hudMin(hudMax(n / 2, 6), (hudMin(vw, vh) - 1) / 8);
    const int availableWidth = hudMax(1, vw - out.margin * 2);
    const int availableHeight = hudMax(1, vh - out.margin * 2);
    out.width = hudMin(availableWidth, hudMax(n * 46, vw * 3 / 4));
    out.inset = hudMin(n, (out.width - 1) / 4);
    out.contentWidth = hudMax(1, out.width - out.inset * 2);
    const int header = hudMax(0, requestedHeader), footer = hudMax(0, requestedFooter);
    const int row = hudMax(1, requestedRow);
    out.height = hudMin(availableHeight, header + footer + row * hudMax(1, rows));
    out.headerHeight = header;
    out.footerHeight = footer;
    if(header + footer + row > out.height)
    {
        // This fallback is reached only when even the minimum local font does
        // not fit. Scale glyph drawing inside allocated regions, never overlap
        // or drop explanatory text. Physical TableView rows remain authoritative.
        const int minimumMenu = hudMax(1, hudMin(row, out.height / 3));
        const int availableText = out.height - minimumMenu;
        out.headerHeight = header + footer ? availableText * header / (header + footer) : 0;
        out.footerHeight = availableText - out.headerHeight;
    }
    out.menuHeight = hudMax(1, out.height - out.headerHeight - out.footerHeight);
    out.headerScale = header ? float(out.headerHeight) / header : 1.f;
    out.footerScale = footer ? float(out.footerHeight) / footer : 1.f;
    return out;
}
}
