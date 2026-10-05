#include <cstdio>
#include <cstring>
#include <string>
#include "../native/station_game_details.h"

static unsigned checks = 0, failures = 0;
static void check(bool value, const char* label) {
 ++checks;
 if (!value) { ++failures; std::printf("FAIL %s\n", label); }
}
static const StationGameDetails* linear(const char* id) {
 for (int i = 0; i < NSTATIONGAMEDETAILS; ++i)
  if (std::strcmp(id, stationGameDetails[i].id) == 0) return stationGameDetails + i;
 return nullptr;
}
int main() {
 check(NSTATIONGAMEDETAILS == 2212, "published row count");
 check(!findStationGameDetails(nullptr), "null identity");
 check(!findStationGameDetails(""), "empty identity");
 check(!findStationGameDetails("00000000"), "unknown before first");
 check(!findStationGameDetails("zzzzzzzz"), "unknown after last");
 int missingPlayers = 0, missingRating = 0, zeroRating = 0;
 for (int i = 0; i < NSTATIONGAMEDETAILS; ++i) {
  const auto* row = stationGameDetails + i;
  check(findStationGameDetails(row->id) == row, "every exact row is found");
  check(i == 0 || std::strcmp(stationGameDetails[i - 1].id, row->id) < 0, "strict sorted unique IDs");
  check(row->ratingThousandths >= -1 && row->ratingThousandths <= 1000, "bounded rating");
  std::string unknown = std::string(row->id) + "_not_published";
  check(!findStationGameDetails(unknown.c_str()), "suffix cannot select another game");
  const std::string alias = std::strncmp(row->id, "station_", 8) == 0
      ? std::string(row->id + 8) : std::string("station_") + row->id;
  check(findStationGameDetails(alias.c_str()) == linear(alias.c_str()), "prefix aliases require independent exact published IDs");
  if (!*row->players) ++missingPlayers;
  if (row->ratingThousandths == -1) ++missingRating;
  if (row->ratingThousandths == 0) ++zeroRating;
 }
 check(missingPlayers == 64, "no invented player count for missing data");
 check(missingRating == 226, "missing ratings remain unknown");
 check(zeroRating == 9, "explicit zero ratings remain zero");
 const auto* n64 = findStationGameDetails("station_c16309c829ad81a41da0b4cb7236a4fb");
 check(n64 && std::strcmp(n64->players, "4") == 0, "published N64 player count");
 const auto* alternate = findStationGameDetails("station_23c83c0af84a554b338c8eac2876cd8c");
 check(alternate && !*alternate->players && alternate->ratingThousandths == -1, "alternate ROM stays unknown");
 std::printf("%u checks; %u failures; all %d published rows exercised\n", checks, failures, NSTATIONGAMEDETAILS);
 return failures ? 1 : 0;
}
