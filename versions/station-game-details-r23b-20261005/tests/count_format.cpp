#include <cstring>
#include <cstdio>
#include <limits>
using U=unsigned long;
static int failures;
static void check(U visibleCount,const char*expected){char countLabel[48]={},digits[24]={};U remainingCount=visibleCount;int length=0;
  do{digits[length++]=(char)('0'+remainingCount%10);remainingCount/=10;}while(remainingCount&&length<23);
  for(int i=0;i<length;i++)countLabel[i]=digits[length-i-1];
  const char*suffixCount=visibleCount==1?" jogo":" jogos";memcpy(countLabel+length,suffixCount,strlen(suffixCount)+1);
  if(std::strcmp(countLabel,expected)){failures++;std::printf("unexpected count: %s\n",countLabel);}}
int main(){check(0,"0 jogos");check(1,"1 jogo");check(157,"157 jogos");check(644,"644 jogos");check(887,"887 jogos");check(2212,"2212 jogos");check(40000,"40000 jogos");check(4294967295UL,"4294967295 jogos");std::printf("8 count formatting checks; %d failures\n",failures);return failures;}
