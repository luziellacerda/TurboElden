#include "native/native_catalog_identity.h"
static_assert(catalogIdentityChanged(-1,0,0,0,0));
static_assert(catalogIdentityChanged(-1,0,0,100,232));
static_assert(!catalogIdentityChanged(1,100,232,100,232));
static_assert(!catalogIdentityChanged(4000,100,232,100,232));
static_assert(catalogIdentityChanged(2,100,232,200,232));
static_assert(catalogIdentityChanged(3,200,232,100,232));
static_assert(catalogIdentityChanged(1,100,232,100,464));
static_assert(catalogIdentityChanged(1,100,232,0,0));
static_assert(!catalogIdentityChanged(0,0,0,0,0));
int main() { return 0; }
