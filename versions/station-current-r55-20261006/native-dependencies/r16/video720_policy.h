// Pure policy shared with host regression tests. Error retry and idle pacing stay separate.
#pragma once
static constexpr unsigned video720TextureBudget=8;
static constexpr unsigned video720TextureBytes=720u*720u*2u;
static constexpr unsigned video720MaxRetainedBytes=video720TextureBudget*video720TextureBytes;
static bool video720Older(unsigned a,unsigned b){return static_cast<int>(a-b)<0;}
