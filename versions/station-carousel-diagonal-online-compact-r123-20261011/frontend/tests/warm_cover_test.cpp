#include "../station_cover_warmstart.hpp"
#include "../station_catalog_row.hpp"
#include <iostream>
#include <stdexcept>

namespace {
int checks=0;
void check(bool value,const char* message){++checks;if(!value)throw std::runtime_error(message);}
struct Fixture {
 std::string id,coverId,coverPath;
 bool coverReady=false,coverFailed=false,coverPending=false;
};
std::string row(std::initializer_list<std::string> fields){std::string value;for(const auto& field:fields){value+=field;value.push_back('\0');}return value;}
bool rejects(const std::string& input){try{(void)station::parseNativeCatalogRow(input);return false;}catch(const std::runtime_error&){return true;}}
}
int main(){
 uint64_t revision=0;
 check(station::parseCoverRevision("7",&revision)&&revision==7,"revision parse");
 check(!station::parseCoverRevision("",&revision),"empty revision rejected");
 check(!station::parseCoverRevision("0",&revision),"zero revision rejected");
 check(!station::parseCoverRevision("7x",&revision),"mixed revision rejected");
 check(!station::parseCoverRevision("18446744073709551616",&revision),"overflow rejected");
 const std::string valid="/data/user/0/org.turboramastation.frontend/no_backup/station-v2/covers/cover_test_1234-7.img";
 const std::string legacyPath="/data/data/org.turboramastation.frontend/no_backup/station-covers/cover_test_1234.webp";
 check(station::validWarmCoverPath(valid,"cover_test_1234",7),"exact private cache path accepted");
 check(station::validWarmCoverPath(legacyPath,"cover_test_1234",7),"exact private legacy path accepted after Java revision proof");
 check(!station::validWarmCoverPath("/data/user/0/org.turboramastation.frontend/no_backup/other/station-covers/cover_test_1234.webp","cover_test_1234",7),"nested lookalike legacy path rejected");
 check(!station::validWarmCoverPath("/data/user/0/org.emulationstation.frontend/no_backup/station-v2/covers/cover_test_1234-7.img","cover_test_1234",7),"different package root rejected");
 check(!station::validWarmCoverPath("relative/cover_test_1234-7.img","cover_test_1234",7),"relative path rejected");
 check(!station::validWarmCoverPath("/data/../cover_test_1234-7.img","cover_test_1234",7),"traversal rejected");
 check(!station::validWarmCoverPath(valid,"other_cover_1234",7),"wrong cover rejected");
 check(!station::validWarmCoverPath(valid,"cover_test_1234",8),"wrong revision rejected");
 Fixture previous{"item_test_1234","cover_test_1234",valid,true,false,false};
 Fixture next{"item_test_1234","cover_test_1234","",false,true,true};
 check(station::preserveWarmCover(previous,7,next,7),"same identity preserves warm path");
 check(next.coverPath==valid&&next.coverReady&&!next.coverFailed&&!next.coverPending,"preserved state is ready");
 Fixture changedCover{"item_test_1234","cover_other_1234","",false,false,false};
 check(!station::preserveWarmCover(previous,7,changedCover,7)&&changedCover.coverPath.empty(),"changed cover cannot inherit");
 Fixture changedRevision{"item_test_1234","cover_test_1234","",false,false,false};
 check(!station::preserveWarmCover(previous,7,changedRevision,8)&&changedRevision.coverPath.empty(),"changed revision cannot inherit");
 Fixture alreadyWarm{"item_test_1234","cover_test_1234","/new/path.img",true,false,false};
 check(!station::preserveWarmCover(previous,7,alreadyWarm,7)&&alreadyWarm.coverPath=="/new/path.img","published warm path wins");
 const auto legacy=station::parseNativeCatalogRow(row({"item_test_1234","Game","SNES","snes","cover_test_1234",""}));
 check(legacy.coverRevision==0&&legacy.coverPath.empty()&&legacy.folderPath.empty(),"legacy six-field row remains accepted");
 const auto r112=station::parseNativeCatalogRow(row({"item_test_1234","Game","SNES","snes","cover_test_1234","","Collection","Description"}));
 check(r112.coverRevision==0&&r112.coverPath.empty()&&r112.folderPath=="Collection","R112 row remains accepted");
 const auto r113=station::parseNativeCatalogRow(row({"item_test_1234","Game","SNES","snes","cover_test_1234","","Collection","Description","7",valid}));
 check(r113.coverRevision==7&&r113.coverPath==valid,"R113 row initializes revision and warm path");
 const auto cold=station::parseNativeCatalogRow(row({"item_test_1234","Game","SNES","snes","cover_test_1234","","","","7",""}));
 check(cold.coverRevision==7&&cold.coverPath.empty(),"R113 cache miss keeps an empty optional path");
 check(rejects(row({"item_test_1234","Game","SNES","snes","cover_test_1234","","","","bad",""})),"malformed revision rejected");
 check(rejects(row({"item_test_1234","Game","SNES","snes","cover_test_1234","","","","7","/wrong.img"})),"malformed path rejected");
 std::string incomplete=row({"item_test_1234","Game","SNES","snes","cover_test_1234","","","","7"});incomplete.pop_back();
 check(rejects(incomplete),"unterminated optional field rejected");
 check(rejects(row({"item_test_1234","Game","SNES","snes","cover_test_1234","","","","7","", "extra"})),"unexpected tail rejected");
 std::cout<<"PASS "<<checks<<" native warm-cover checks\n";
}
