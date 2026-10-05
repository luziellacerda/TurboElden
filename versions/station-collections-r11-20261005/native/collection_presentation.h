#pragma once
// Presentation only: no URLs, IO, threads, catalogue mutation or invented metadata.
struct CollectionText {
 char* data;unsigned long capacity,used;
 CollectionText(char* value,unsigned long size):data(value),capacity(size),used(0){if(capacity)data[0]=0;}
 void append(const char* text){
  if(!text||!capacity)return;
  while(*text){
   unsigned char c=(unsigned char)*text;unsigned n=c<0x80?1:c<0xe0?2:c<0xf0?3:4;
   if(used+n>=capacity)return;
   for(unsigned i=1;i<n;i++)if(!text[i]||((unsigned char)text[i]&0xc0)!=0x80)return;
   for(unsigned i=0;i<n;i++)data[used++]=*text++;
   data[used]=0;
  }
 }
 void number(unsigned long n){char buffer[24],reverse[24];int i=0,j=0;do{reverse[i++]=(char)('0'+n%10);n/=10;}while(n);while(i)buffer[j++]=reverse[--i];buffer[j]=0;append(buffer);}
};
static const char*collectionLeafName(const char*path){const char*leaf=path;for(const char*p=path;*p;p++)if(*p=='/')leaf=p+1;return leaf;}
static bool collectionHasPath(const char*parent,const char*path,bool all,bool direct){
 if(all)return true;
 while(*parent&&*path&&*parent==*path){parent++;path++;}
 return !*parent&&(!*path||(!direct&&*path=='/'));
}
static void collectionSynopsis(char*output,unsigned long size,const char*name,const char*platform,unsigned long count,int kind,const char*const*examples,unsigned exampleCount){
 CollectionText text(output,size);
 if(kind==2){text.append("A biblioteca completa de ");text.append(platform);text.append(" em uma única lista. ");text.number(count);text.append(count==1?" jogo disponível, incluindo a seleção da raiz e das coleções.":" jogos disponíveis, incluindo os títulos da raiz e das coleções.");}
 else {text.append("Coleção ");text.append(name);text.append(". ");text.number(count);text.append(count==1?" jogo de ":" jogos de ");text.append(platform);text.append(kind==1?" organizados diretamente nesta pasta.":" reunidos nesta seleção e em suas subcoleções, quando houver.");}
 if(exampleCount){text.append("\n\nEntre os títulos: ");for(unsigned i=0;i<exampleCount;i++){if(i)text.append("; ");text.append(examples[i]);}text.append(".");}
 text.append(kind==2?"\n\nAbra para pesquisar, baixar ou jogar em toda a biblioteca.":"\n\nAbra para explorar esta coleção, escolher um jogo e continuar sua sessão.");
}
