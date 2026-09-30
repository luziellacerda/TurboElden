#include <jni.h>
#include <archive.h>
#include <archive_entry.h>
#include <android/log.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>

static void archive_diagnostic(const char *operation,struct archive *a,const char *name,int status,long long expected,unsigned long long received){
 const char *format=archive_format_name(a),*detail=archive_error_string(a);
 __android_log_print(ANDROID_LOG_ERROR,"TurboVitaArchive","%s: format=%s entry=%s status=%d errno=%d expected=%lld read=%llu detail=%s",operation,format?format:"unknown",name?name:"(none)",status,archive_errno(a),expected,received,detail?detail:"(none)");
}
static int skip_entry(struct archive *a,const char *name){
 int status=archive_read_data_skip(a);if(status==ARCHIVE_OK)return 1;
 archive_diagnostic("skip",a,name,status,-1,0);return 0;
}
static int clean_name(const char *raw,char *out,size_t size){
 if(!raw||strlen(raw)>=size)return 0;
 size_t n=0;while(*raw){char c=*raw++;out[n++]=c=='\\'?'/':c;}out[n]=0;
 if(out[0]=='/'||strchr(out,':'))return 0;
 const char *p=out;
 while(*p){const char *end=strchr(p,'/');size_t len=end?(size_t)(end-p):strlen(p);if(len==2&&p[0]=='.'&&p[1]=='.')return 0;if(!end)break;p=end+1;}
 return 1;
}
static struct archive *open_rar(const char *path){
 struct archive *a=archive_read_new();archive_read_support_filter_all(a);archive_read_support_format_rar(a);archive_read_support_format_rar5(a);
 int status=archive_read_open_filename(a,path,128*1024);
 if(status!=ARCHIVE_OK){archive_diagnostic("open",a,NULL,status,-1,0);archive_read_free(a);return NULL;}return a;
}
JNIEXPORT jstring JNICALL Java_org_emulationstation_frontend_VitaBootstrap_convertRar(JNIEnv *env,jclass cls,jstring input,jstring output,jobject progress){
 (void)cls;const char *src=(*env)->GetStringUTFChars(env,input,NULL),*dst=(*env)->GetStringUTFChars(env,output,NULL);
 char error[512]={0},root[4096]={0},name[4096];int found=0,result=0,files=0,lastPercent=-1;long long total=0;
 struct archive *a=NULL,*w=NULL;struct archive_entry *entry;struct stat st={0};char *buffer=NULL;
 jclass cb=(*env)->GetObjectClass(env,progress);jmethodID notify=(*env)->GetMethodID(env,cb,"onProgress","(ILjava/lang/String;)V"),cancel=(*env)->GetMethodID(env,cb,"isCancelled","()Z");
 if(!src||!dst||!notify||!cancel){snprintf(error,sizeof(error),"Falha ao preparar a leitura do pacote.");goto done;}
 a=open_rar(src);if(!a){snprintf(error,sizeof(error),"Não foi possível abrir o arquivo RAR.");goto done;}
 while((result=archive_read_next_header(a,&entry))==ARCHIVE_OK){
  if((*env)->CallBooleanMethod(env,progress,cancel)){snprintf(error,sizeof(error),"Operação cancelada.");goto done;}
  if(!clean_name(archive_entry_pathname(entry),name,sizeof(name))){snprintf(error,sizeof(error),"O pacote contém um caminho inválido.");goto done;}
  if(archive_entry_is_encrypted(entry)>0){archive_diagnostic("encrypted-entry",a,name,ARCHIVE_FAILED,-1,0);snprintf(error,sizeof(error),"O pacote PS Vita contém arquivos protegidos por senha. Use uma cópia sem senha.");goto done;}
  if(archive_entry_size(entry)>0)total+=archive_entry_size(entry);
  const char *sfo=strstr(name,"sce_sys/param.sfo");
  if(sfo&&strcmp(sfo,"sce_sys/param.sfo")==0&&(sfo==name||sfo[-1]=='/')){
   size_t len=(size_t)(sfo-name);if(found&&!(strlen(root)==len&&!memcmp(root,name,len))){snprintf(error,sizeof(error),"O RAR contém mais de um título. Separe os jogos antes de instalar.");goto done;}
   memcpy(root,name,len);root[len]=0;found=1;
  }
  if(!skip_entry(a,name)){snprintf(error,sizeof(error),"Não foi possível ler o pacote PS Vita.");goto done;}
 }
 if(result!=ARCHIVE_EOF){archive_diagnostic("scan-header",a,NULL,result,-1,0);snprintf(error,sizeof(error),"Não foi possível ler o pacote PS Vita.");goto done;}
 if(!found){snprintf(error,sizeof(error),"O RAR não contém uma pasta válida de jogo PS Vita (sce_sys/param.sfo).");goto done;}
 archive_read_free(a);a=NULL;
 char parent[4096];if(strlen(dst)>=sizeof(parent)){snprintf(error,sizeof(error),"Caminho temporário inválido.");goto done;}strcpy(parent,dst);char *slash=strrchr(parent,'/');if(slash)*slash=0;
 struct statvfs space;if(statvfs(parent,&space)==0&&total>0&&(unsigned long long)total*2+67108864ULL>(unsigned long long)space.f_bavail*space.f_frsize){snprintf(error,sizeof(error),"Espaço insuficiente para preparar e instalar o jogo PS Vita.");goto done;}
 a=open_rar(src);if(!a){snprintf(error,sizeof(error),"Falha ao reabrir o RAR.");goto done;}
 w=archive_write_new();archive_write_set_format_zip(w);archive_write_set_options(w,"zip:compression=store");
 if(archive_write_open_filename(w,dst)!=ARCHIVE_OK){snprintf(error,sizeof(error),"Não foi possível criar o pacote temporário.");goto done;}
 stat(src,&st);buffer=malloc(128*1024);if(!buffer){snprintf(error,sizeof(error),"Memória insuficiente para preparar o pacote.");goto done;}
 while((result=archive_read_next_header(a,&entry))==ARCHIVE_OK){
  if(!clean_name(archive_entry_pathname(entry),name,sizeof(name))){snprintf(error,sizeof(error),"Caminho inválido no pacote.");goto done;}
  if(archive_entry_is_encrypted(entry)>0){archive_diagnostic("encrypted-entry",a,name,ARCHIVE_FAILED,-1,0);snprintf(error,sizeof(error),"O pacote PS Vita contém arquivos protegidos por senha. Use uma cópia sem senha.");goto done;}
  size_t prefix=strlen(root);if(strncmp(name,root,prefix)){if(!skip_entry(a,name)){snprintf(error,sizeof(error),"Não foi possível ler o pacote PS Vita.");goto done;}continue;}
  const char *relative=name+prefix;if(!*relative){if(!skip_entry(a,name)){snprintf(error,sizeof(error),"Não foi possível ler o pacote PS Vita.");goto done;}continue;}
  if(archive_entry_symlink(entry)||archive_entry_hardlink(entry)){snprintf(error,sizeof(error),"Links internos não são aceitos no pacote do jogo.");goto done;}
  if(archive_entry_filetype(entry)!=AE_IFREG&&archive_entry_filetype(entry)!=AE_IFDIR){if(!skip_entry(a,name)){snprintf(error,sizeof(error),"Não foi possível ler o pacote PS Vita.");goto done;}continue;}
  archive_entry_set_pathname(entry,relative);archive_entry_set_perm(entry,archive_entry_filetype(entry)==AE_IFDIR?0700:0600);
  if(archive_write_header(w,entry)<ARCHIVE_OK){snprintf(error,sizeof(error),"Falha ao gravar o pacote temporário.");goto done;}
  if(archive_entry_filetype(entry)==AE_IFDIR){
   if(!skip_entry(a,name)){snprintf(error,sizeof(error),"Não foi possível ler o pacote PS Vita.");goto done;}
   if(archive_write_finish_entry(w)<ARCHIVE_OK){snprintf(error,sizeof(error),"Erro ao finalizar uma pasta do pacote.");goto done;}files++;continue;
  }
  long long expected=archive_entry_size_is_set(entry)?(long long)archive_entry_size(entry):-1;
  unsigned long long received=0;
  la_ssize_t n;
  while((n=archive_read_data(a,buffer,128*1024))>0){
   if((*env)->CallBooleanMethod(env,progress,cancel)){snprintf(error,sizeof(error),"Operação cancelada.");goto done;}
   received+=(unsigned long long)n;
   if(expected>=0&&received>(unsigned long long)expected){archive_diagnostic("entry-size-exceeded",a,name,ARCHIVE_FAILED,expected,received);snprintf(error,sizeof(error),"O tamanho lido de um arquivo não corresponde ao declarado no pacote PS Vita.");goto done;}
   if(archive_write_data(w,buffer,(size_t)n)!=n){snprintf(error,sizeof(error),"Espaço insuficiente ou erro ao gravar o pacote.");goto done;}
   int p=st.st_size>0?(int)(archive_filter_bytes(a,-1)*100/st.st_size):0;if(p>99)p=99;
   if(p!=lastPercent){lastPercent=p;jstring msg=(*env)->NewStringUTF(env,"Preparando pacote PS Vita");(*env)->CallVoidMethod(env,progress,notify,p,msg);(*env)->DeleteLocalRef(env,msg);if((*env)->ExceptionCheck(env))goto done;}
  }
  if(n<0){archive_diagnostic("read-data",a,name,(int)n,expected,received);snprintf(error,sizeof(error),"Não foi possível ler um arquivo do pacote PS Vita.");goto done;}
  if(expected>=0&&received!=(unsigned long long)expected){archive_diagnostic("entry-size-mismatch",a,name,ARCHIVE_FAILED,expected,received);snprintf(error,sizeof(error),"O tamanho lido de um arquivo não corresponde ao declarado no pacote PS Vita.");goto done;}
  if(archive_write_finish_entry(w)<ARCHIVE_OK){snprintf(error,sizeof(error),"Erro ao finalizar um arquivo do pacote.");goto done;}files++;
 }
 if(result!=ARCHIVE_EOF){archive_diagnostic("read-header",a,NULL,result,-1,0);snprintf(error,sizeof(error),"Não foi possível ler o pacote PS Vita.");goto done;}
 if(!files){snprintf(error,sizeof(error),"Falha na leitura do pacote PS Vita.");goto done;}
 if(archive_write_close(w)!=ARCHIVE_OK)snprintf(error,sizeof(error),"Não foi possível concluir o pacote temporário.");
done:
 if(a)archive_read_free(a);if(w)archive_write_free(w);free(buffer);
 if(error[0]&&dst)unlink(dst);
 if(src)(*env)->ReleaseStringUTFChars(env,input,src);if(dst)(*env)->ReleaseStringUTFChars(env,output,dst);if(cb)(*env)->DeleteLocalRef(env,cb);
 return error[0]?(*env)->NewStringUTF(env,error):NULL;
}
