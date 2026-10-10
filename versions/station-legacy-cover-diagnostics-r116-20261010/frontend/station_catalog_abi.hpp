#pragma once
#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>
// Read-only renderer contract recovered from libmain a1ae357d. No network URLs are stored.
// R113 extends only the bounded JNI row tail (revision, optional private cover path).
// Item and Catalog remain byte-for-byte ABI compatible with the retained renderer.
namespace station {
struct Item {
 std::string id,name,unusedGameUrl,coverId,platform,folder,fileName;
 bool installed=false;
 uint8_t installedPadding[7]{};
 std::string localPath,coverPath;
 bool coverFailed=false,coverReady=false,coverPending=false;
 uint8_t trailingPadding[5]{};
};
struct Progress {bool active=false;uint8_t padding[7]{};int64_t received=0,total=-1;std::string error;};
struct Catalog {
 uint8_t engineState[0x50]; // Bundled engine state belongs to the unchanged renderer/runtime.
 int32_t state;uint32_t statePadding;
 std::string error,unusedCatalogUrl;
 std::vector<Item> items;
 void* unusedRequest;
 uint32_t revision;uint32_t revisionPadding;
 uint64_t installedCount;
 uint8_t reserved[0x18];
 std::vector<Item> unusedPending;
 uint8_t unusedCovers[0x18];
 std::vector<size_t> priorities;
 uint8_t tail[0x20];
};
static_assert(sizeof(std::string)==24,"Requires Android libc++ arm64 ABI");
static_assert(sizeof(Item)==0xe8 && offsetof(Item,localPath)==0xb0 && offsetof(Item,coverPath)==0xc8);
static_assert(offsetof(Item,installed)==0xa8 && offsetof(Item,coverReady)==0xe1);
static_assert(sizeof(Progress)==48 && offsetof(Progress,error)==24);
static_assert(sizeof(Catalog)==0x138 && offsetof(Catalog,items)==0x88 && offsetof(Catalog,priorities)==0x100);
static_assert(offsetof(Catalog,revision)==0xa8 && offsetof(Catalog,installedCount)==0xb0);
}
