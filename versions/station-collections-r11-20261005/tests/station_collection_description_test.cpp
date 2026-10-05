#include <cassert>
#include <cstring>
#include <iostream>
#include "collection_presentation.h"
static bool utf8(const char*s){while(*s){unsigned char c=(unsigned char)*s++;unsigned n=c<0x80?0:c<0xe0?1:c<0xf0?2:3;for(unsigned i=0;i<n;i++)if(!*s||((unsigned char)*s++&0xc0)!=0x80)return false;}return true;}
int main(){int count=0;auto check=[&](bool v){assert(v);count++;};
 check(!strcmp(collectionLeafName("RPG/Traduções"),"Traduções"));check(!strcmp(collectionLeafName("RPG"),"RPG"));
 check(collectionHasPath("RPG","RPG/Traduções",false,false));check(!collectionHasPath("RPG","RPG2",false,false));
 check(!collectionHasPath("RPG","RPG/Traduções",false,true));check(collectionHasPath("RPG","RPG",false,true));check(collectionHasPath("","",true,false));
 const char*examples[]={"Ação em português", "Corrida clássica"};char text[2048];
 collectionSynopsis(text,sizeof(text),"Traduções","Super Nintendo",2,0,examples,2);
 check(strstr(text,"Coleção Traduções.")!=nullptr);check(strstr(text,examples[0])!=nullptr);check(strstr(text,"2 jogos")!=nullptr);
 for(unsigned size=1;size<=2048;size++){memset(text,0x55,sizeof(text));collectionSynopsis(text,size,"Traduções","Super Nintendo",2,0,examples,2);check(memchr(text,0,size)!=nullptr);check(utf8(text));if(size<sizeof(text))check(text[size]==0x55);}
 std::cout<<"PASS "<<count<<" collection description, exact path and bounded UTF-8 checks\n";
}