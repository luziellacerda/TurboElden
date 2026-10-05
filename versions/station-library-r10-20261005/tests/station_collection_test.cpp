#include <cassert>
#include <cstdio>
#include <map>
#include <string>
#include <vector>
#include "station_collections.hpp"
struct Item {std::string id,platform,coverPath;};
int main(){
 int checks=0;auto check=[&](bool ok){assert(ok);checks++;};
 for(std::string s:{"","RPG","RPG/Traduções","日本語 🎮"})check(station::validCollectionPath(s));
 for(std::string s:{"/RPG","RPG/","RPG//PT",".","..","RPG/..","a\\b"," ","a\nb","a/b/c/d/e/f/g/h/i"})check(!station::validCollectionPath(s));
 check(!station::collectionContains("RPG","RPG2"));check(station::collectionContains("RPG","RPG/PT"));
 std::vector<Item> items={{"root","snes",""},{"rpg1","snes","cover1"},{"rpg2","snes","cover2"},{"deep","snes","cover3"},{"other","mega","cover4"},{"rpg3","snes","cover5"}};
 std::map<std::string,std::string> paths={{"rpg1","RPG"},{"rpg2","RPG/Traduções"},{"deep","RPG/Traduções/Selecionados"},{"other","RPG"},{"rpg3","RPG2"}};
 auto root=station::collectionListing(items,paths,"snes","");check(root.direct==1);check(root.total==5);check(root.children.size()==2);check(root.children.at("RPG").count==3);check(root.children.at("RPG").cover=="cover1");
 auto rpg=station::collectionListing(items,paths,"snes","RPG");check(rpg.direct==1);check(rpg.total==3);check(rpg.children.size()==1);check(rpg.children.at("Traduções").count==2);check(rpg.children.at("Traduções").path=="RPG/Traduções");
 auto leaf=station::collectionListing(items,paths,"snes","RPG/Traduções/Selecionados");check(leaf.direct==1);check(leaf.children.empty());
 auto missing=station::collectionListing(items,paths,"snes","missing");check(missing.total==0);check(missing.children.empty());
 paths.clear();auto flat=station::collectionListing(items,paths,"snes","");check(flat.total==5);check(flat.direct==5);check(flat.children.empty());
 items.clear();for(int i=0;i<4096;i++){auto id=std::to_string(i);items.push_back({id,"snes",""});paths[id]="Pasta "+std::to_string(i%16)+"/Sub "+std::to_string(i%64);}
 auto large=station::collectionListing(items,paths,"snes","");check(large.total==4096);check(large.children.size()==16);size_t count=0;for(auto& pair:large.children)count+=pair.second.count;check(count==4096);
 puts(("PASS "+std::to_string(checks)+" native collection checks; platform isolation, nesting, root, leaf, prefix and 4096 entries").c_str());
}
