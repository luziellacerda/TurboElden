/* TurboStations native HUD, based on the Imagine/EmuFramework view APIs.
 * SPDX-License-Identifier: GPL-3.0-or-later
 * Upstream Imagine/EmuFramework copyright Robert Broglia; retained in source.
 */
#pragma once

#include <emuframework/defs.hh>
#ifndef IG_USE_MODULE_IMAGINE
#include <imagine/gui/viewDefs.hh>
#endif

namespace IG::Input { class Event; }

namespace EmuEx
{
class EmuApp;
// Invoke from the engine's semantic menu actions, never from screen coordinates.
void showStationHud(EmuApp&, IG::ViewAttachParams, const IG::Input::Event&);
}
