#include "../src/native/station_synopsis_pages.hpp"
#include <cassert>
#include <iostream>
int main(){
 assert(station::synopsisPages("").empty());assert(station::synopsisPages("Sinopse")=="Sinopse");
 std::string longText;for(int i=0;i<600;i++)longText+="ação ";
 auto pages=station::synopsisPages(longText);assert(pages.find('\f')!=std::string::npos);
 for(size_t i=0;i<pages.size();i++)if(pages[i]=='\f')assert(i+1<pages.size()&&(static_cast<unsigned char>(pages[i+1])&0xc0)!=0x80);
 auto unicode=station::synopsisPages(std::string(799,'a')+"ação");assert(unicode.find("ação")!=std::string::npos);
 std::cout<<"PASS native synopsis paging, word and UTF-8 boundaries\n";
}
