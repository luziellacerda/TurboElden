#pragma once
#include "station_cover_warmstart.hpp"
#include <array>
#include <stdexcept>
#include <string>

namespace station {
struct NativeCatalogRow {
 std::array<std::string,6> fields;
 std::string folderPath,description,coverPath;
 uint64_t coverRevision=0;
};

inline std::string catalogRowField(const std::string& row,size_t* offset,const char* failure,size_t limit=static_cast<size_t>(-1)){
 const size_t end=row.find('\0',*offset);
 if(end==std::string::npos||end-*offset>limit)throw std::runtime_error(failure);
 std::string value=row.substr(*offset,end-*offset);*offset=end+1;return value;
}

/** Parses the actual bounded NUL ABI shared by legacy R112 and R113. */
inline NativeCatalogRow parseNativeCatalogRow(const std::string& row){
 NativeCatalogRow parsed;size_t offset=0;
 for(auto& field:parsed.fields)field=catalogRowField(row,&offset,"Incomplete native catalog row");
 if(offset<row.size())parsed.folderPath=catalogRowField(row,&offset,"Incomplete collection path");
 if(offset<row.size())parsed.description=catalogRowField(row,&offset,"Invalid description",8000);
 if(offset<row.size()){
  const std::string revision=catalogRowField(row,&offset,"Incomplete cover revision");
  if(!parseCoverRevision(revision,&parsed.coverRevision))throw std::runtime_error("Invalid cover revision");
 }
 if(offset<row.size()){
  parsed.coverPath=catalogRowField(row,&offset,"Incomplete warm cover path",4096);
  if(!parsed.coverPath.empty()&&!validWarmCoverPath(parsed.coverPath,parsed.fields[4],parsed.coverRevision))
   throw std::runtime_error("Invalid warm cover path");
 }
 if(offset!=row.size())throw std::runtime_error("Unexpected native catalog row field");
 return parsed;
}
}
