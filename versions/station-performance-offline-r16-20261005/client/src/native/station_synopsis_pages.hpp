#pragma once
#include <string>
#include <algorithm>
namespace station {
// Word boundaries and UTF-8 codepoints survive paging into the retained native renderer.
inline std::string synopsisPages(const std::string& text) {
 std::string result;size_t start=0;
 while(start<text.size()) {
  size_t end=std::min(start+800,text.size());
  if(end<text.size()) {
   while(end>start&&(static_cast<unsigned char>(text[end])&0xc0)==0x80)--end;
   size_t word=text.find_last_of(" \n\t",end);
   if(word!=std::string::npos&&word>start+400)end=word;
   else {
    size_t next=text.find_first_of(" \n\t",end);
    end=std::min(next==std::string::npos?text.size():next,std::min(start+1200,text.size()));
    while(end<text.size()&&end>start&&(static_cast<unsigned char>(text[end])&0xc0)==0x80)--end;
   }
  }
  result.append(text,start,end-start);start=end;
  while(start<text.size()&&(text[start]==' '||text[start]=='\n'||text[start]=='\t'))++start;
  if(start<text.size())result+='\f';
 }
 return result;
}
}
