#pragma once
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <mutex>
#include <string>
#include <utility>
namespace station {
// In-memory presentation data from the existing authenticated Java pipeline.
// This class neither authorizes access nor writes the legacy local profile.
class ProfileName final {
 std::mutex mutex_;
 std::string name_;
 std::atomic<uint64_t> revision_{0};
public:
 void publish(std::string value) {
  std::lock_guard<std::mutex> guard(mutex_);
  uint64_t current=revision_.load(std::memory_order_relaxed);
  if(current!=0 && name_==value)return;
  name_=std::move(value);
  const uint64_t next=current+1;
  revision_.store(next==0?1:next,std::memory_order_release);
 }
 uint64_t revision()const noexcept {return revision_.load(std::memory_order_acquire);}
 bool copyName(char* destination,size_t capacity,uint64_t* revision) {
  if(destination && capacity)destination[0]='\0';
  if(revision)*revision=0;
  if(!destination || !capacity || !revision)return false;
  std::lock_guard<std::mutex> guard(mutex_);
  if(name_.size()>=capacity)return false;
  std::memcpy(destination,name_.c_str(),name_.size()+1);
  *revision=revision_.load(std::memory_order_relaxed);
  return true;
 }
};
}
