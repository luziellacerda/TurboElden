#pragma once
// A finished selection stays on its retained frame; selecting another cell
// (even with the same clip) or entering the carousel creates a new visit.
struct StationVideoOncePolicy {
 const void*owner=nullptr;const char*asset=nullptr;
 int cursor=-1;unsigned long long mapped=0;bool folder=false,observed=false,completed=false;
 static constexpr bool equal(const char*a,const char*b){if(!a||!b)return a==b;while(*a&&*a==*b){++a;++b;}return *a==*b;}
 constexpr bool observe(const void*p,int c,unsigned long long m,bool f,const char*a){
  bool changed=!observed||owner!=p||cursor!=c||mapped!=m||folder!=f||!equal(asset,a);
  if(changed){owner=p;cursor=c;mapped=m;folder=f;asset=a;observed=true;completed=false;}
  return changed;
 }
 constexpr void finish(){completed=true;}
 constexpr void reset(){observed=false;completed=false;}
};
