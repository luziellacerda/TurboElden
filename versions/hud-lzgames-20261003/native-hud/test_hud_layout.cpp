// Compile-time tests of the SAME allocation function included by the native HUD.
// No graphics mock, no phone changes, no SDK or standard-library dependency.
#include "EmuFramework/include/emuframework/StationHudLayout.hh"

constexpr bool validLayout(int w, int h, int n, int header, int footer, int row, int rows)
{
    auto a = EmuEx::stationHudLayout(w, h, n, header, footer, row, rows);
    int width = EmuEx::hudMax(1, w), height = EmuEx::hudMax(1, h);
    if(a.margin < 0 || a.width < 1 || a.height < 1 || a.contentWidth < 1 || a.menuHeight < 1) return false;
    if(a.width > width - a.margin * 2 || a.height > height - a.margin * 2) return false;
    if(a.inset < 0 || a.contentWidth != a.width - a.inset * 2) return false;
    if(a.headerHeight < 0 || a.footerHeight < 0) return false;
    if(a.headerHeight + a.menuHeight + a.footerHeight != a.height) return false;
    if(a.headerScale < 0.f || a.headerScale > 1.f || a.footerScale < 0.f || a.footerScale > 1.f) return false;
    if(a.headerScale * header > a.headerHeight + .01f) return false;
    if(a.footerScale * footer > a.footerHeight + .01f) return false;
    if(header + footer + row <= height - a.margin * 2)
    {
        if(a.headerScale != 1.f || a.footerScale != 1.f || a.menuHeight < row) return false;
    }
    int physicalRow = EmuEx::hudMin(row, a.menuHeight);
    if(physicalRow < 1 || physicalRow > a.menuHeight) return false;
    return true;
}

constexpr bool allLayouts()
{
    constexpr int sizes[][2]{{640,240},{854,480},{1080,2340},{2340,1080},{320,240},{240,320},{1,1},{0,0}};
    constexpr int fonts[]{16,32,64,128};
    constexpr int noteLines[]{1,2,4,8,20,40};
    constexpr int rows[]{2,5,11};
    for(auto& size : sizes)
        for(int font : fonts)
            for(int lines : noteLines)
                for(int count : rows)
                    if(!validLayout(size[0],size[1],font,font*3,font*(lines+1),font*4,count)) return false;
    return true;
}

static_assert(allLayouts(), "HUD allocations must fit without overlap or negative dimensions");
constexpr auto regression = EmuEx::stationHudLayout(640,240,32,128,176,96,2);
static_assert(regression.menuHeight > 0, "Former -96px menu-height regression");
static_assert(regression.headerHeight + regression.menuHeight + regression.footerHeight == regression.height);
