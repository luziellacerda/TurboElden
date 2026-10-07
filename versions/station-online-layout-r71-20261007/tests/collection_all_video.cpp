#include "collection_video_policy.h"
#include "video720_posters.h"
#include "collection_corner_policy.h"
#include "r53_video_policy.h"
#include "station_menu_frame_policy.h"
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <initializer_list>

static unsigned checks;
static void check(bool value) { ++checks; if (!value) std::abort(); }
static const char *asset = "turbo-system-videos/720-collection-snes-all.mp4";
int main() {
 const char *snes[] = {"Super Nintendo", "Super Nintendo - BR", "snes", "snesbr"};
 const char *neo[] = {"Neo Geo", "neogeo", "neo-geo"};
 check(sizeof(collectionVideoDefinitions)/sizeof(collectionVideoDefinitions[0]) == 13);
 check(sizeof(video720Posters)/sizeof(video720Posters[0]) == 58);
 for (const auto& def : collectionVideoDefinitions) {
  const char *const *aliases = def.family == 0 ? snes : neo;
  const int count = def.family == 0 ? 4 : 3;
  for (int i=0; i<count; ++i) check(collectionVideoFor(aliases[i], def.name, false) == &def);
 }
 for (const char *name : {"Super Nintendo", "snes"}) {
  for (const char *path : {"", "## SUPER MARIO ##", "nested/collection"}) {
   const auto *v = collectionVideoFor(name, path, true);
   check(v && std::strcmp(v->asset, asset) == 0 && v->aspect == 1.f);
  }
  check(!collectionVideoFor(name, "", false));
  check(!collectionVideoFor(name, "Todos os jogos", false));
  check(!collectionVideoFor(name, nullptr, true));
 }
 for (const char *name : {"Super Nintendo - BR", "snesbr", "Neo Geo", "neogeo", "neo-geo", "megadrive", "neogeocd", "", "SNES"})
  check(!collectionVideoFor(name, "", true));
 check(!collectionVideoFor(nullptr, "", true));
 unsigned matches = 0;
 for (const auto& p : video720Posters) {
  check(p.pixels != nullptr);
  if (std::strcmp(p.asset, asset) == 0) { ++matches; check(p.pixels == station_collection_r71_snes_all); }
  for (const auto& other : video720Posters) if (&p != &other) check(std::strcmp(p.asset, other.asset) != 0);
 }
 check(matches == 1);
 check(stationCollectionCorners::radius(true, true, 720, 720, true) > 0);
 check(stationCollectionCorners::radius(true, true, 720, 720, false) == 0);
 check(stationCollectionCorners::radius(true, false, 720, 720, false) > 0);
 check(stationCollectionCorners::radius(false, false, 720, 720, false) == 0);
 check(stationCollectionCorners::allGamesKind(2));
 check(!stationCollectionCorners::allGamesKind(0));
 check(stationMenuFramePolicy::target(false, false, false) == 30);
 check(stationMenuFramePolicy::target(true, false, false) == 15);
 std::printf("PASS %u all-games routes, poster identities, retained-frame count and corner checks\n", checks);
}
