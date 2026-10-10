#include "../native/d0/video720_retained_fastpath_policy.h"

using video720RetainedFastPath::State;
using video720RetainedFastPath::eligible;

constexpr State good={true,true,true,true,true,17};
constexpr State incomplete={false,true,true,true,true,17};
constexpr State slotActive={true,false,true,true,true,17};
constexpr State sourceMissing={true,true,false,true,true,17};
constexpr State contextChanged={true,true,true,false,true,17};
constexpr State programDeleted={true,true,true,true,false,17};
constexpr State programZero={true,true,true,true,true,0};

static_assert(eligible(good),"fully proved retained state must pass");
static_assert(!eligible(incomplete),"unfinished video must fall back");
static_assert(!eligible(slotActive),"active decoder slot must fall back");
static_assert(!eligible(sourceMissing),"missing retained texture must fall back");
static_assert(!eligible(contextChanged),"new EGL context must fall back");
static_assert(!eligible(programDeleted),"invalid preview program must fall back");
static_assert(!eligible(programZero),"missing source program must fall back");

int main(){return eligible(good)?0:1;}
