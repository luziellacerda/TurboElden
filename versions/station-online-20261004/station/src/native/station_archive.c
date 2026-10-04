#define _GNU_SOURCE
#include <jni.h>
#include <archive.h>
#include <archive_entry.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <string.h>
#include <stdint.h>

static void fail(JNIEnv *e,const char *reason) {
    if(!(*e)->ExceptionCheck(e)){jclass c=(*e)->FindClass(e,"java/io/IOException");if(c)(*e)->ThrowNew(e,c,reason);}
}
JNIEXPORT void JNICALL Java_org_emulationstation_frontend_station_StationArchive_readArchive(
    JNIEnv *env,jclass clazz,jstring path,jobject sink,jobject cancel) {
    (void)clazz;const char *name=(*env)->GetStringUTFChars(env,path,0);if(!name)return;
    int fd=open(name,O_RDONLY|O_CLOEXEC|O_NOFOLLOW);(*env)->ReleaseStringUTFChars(env,path,name);
    struct stat info;if(fd<0){fail(env,"Cannot open archive");return;}
    if(fstat(fd,&info)||!S_ISREG(info.st_mode)){close(fd);fail(env,"Archive is not a regular file");return;}
    struct archive *a=archive_read_new();if(!a){close(fd);fail(env,"Archive allocation failed");return;}
    archive_read_support_filter_none(a);
    archive_read_support_format_zip(a);archive_read_support_format_rar(a);
    archive_read_support_format_rar5(a);archive_read_support_format_7zip(a);
    jclass sinkClass=(*env)->GetObjectClass(env,sink),cancelClass=(*env)->GetObjectClass(env,cancel);
    jmethodID begin=(*env)->GetMethodID(env,sinkClass,"begin","([BJZ)V");
    jmethodID data=(*env)->GetMethodID(env,sinkClass,"data","([BI)V");
    jmethodID end=(*env)->GetMethodID(env,sinkClass,"end","()V");
    jmethodID check=(*env)->GetMethodID(env,cancelClass,"check","()V");
    jbyteArray buffer=(*env)->NewByteArray(env,65536);char bytes[65536];
    int status=ARCHIVE_FATAL,entries=0;
    if((*env)->ExceptionCheck(env)||!buffer)goto done;
    if(archive_read_open_fd(a,fd,65536)!=ARCHIVE_OK){fail(env,"Unsupported or corrupt archive");goto done;}
    struct archive_entry *entry;
    for(;;) {
        (*env)->CallVoidMethod(env,cancel,check);if((*env)->ExceptionCheck(env))goto done;
        status=archive_read_next_header(a,&entry);if(status==ARCHIVE_EOF)break;
        if(status!=ARCHIVE_OK||++entries>200000){fail(env,"Invalid or excessive archive members");goto done;}
        int kind=archive_entry_filetype(entry);
        if((kind!=AE_IFREG&&kind!=AE_IFDIR)||archive_entry_symlink(entry)||archive_entry_hardlink(entry)
            ||archive_entry_is_encrypted(entry)>0||archive_entry_sparse_count(entry)>0) {
            fail(env,"Links, sparse, encrypted or special archive members refused");goto done;
        }
        const char *member=archive_entry_pathname_utf8(entry);
        if(!member||!*member||strlen(member)>4096){fail(env,"Archive member name is not valid UTF-8");goto done;}
        la_int64_t size=archive_entry_size(entry);
        if(!archive_entry_size_is_set(entry)||size<0){fail(env,"Archive member has no bounded length");goto done;}
        jbyteArray memberName=(*env)->NewByteArray(env,(jsize)strlen(member));if(!memberName)goto done;
        (*env)->SetByteArrayRegion(env,memberName,0,(jsize)strlen(member),(const jbyte*)member);
        (*env)->CallVoidMethod(env,sink,begin,memberName,(jlong)size,kind==AE_IFDIR?JNI_TRUE:JNI_FALSE);
        (*env)->DeleteLocalRef(env,memberName);if((*env)->ExceptionCheck(env))goto done;
        if(kind==AE_IFREG)for(;;) {
            (*env)->CallVoidMethod(env,cancel,check);if((*env)->ExceptionCheck(env))goto done;
            la_ssize_t count=archive_read_data(a,bytes,sizeof(bytes));
            if(count==0)break;
            if(count<0){fail(env,"Archive member decompression failed");goto done;}
            (*env)->SetByteArrayRegion(env,buffer,0,(jsize)count,(const jbyte*)bytes);
            (*env)->CallVoidMethod(env,sink,data,buffer,(jint)count);if((*env)->ExceptionCheck(env))goto done;
        }
        (*env)->CallVoidMethod(env,sink,end);if((*env)->ExceptionCheck(env))goto done;
    }
    if(archive_read_has_encrypted_entries(a)>0)fail(env,"Encrypted archive refused");
done:
    archive_read_free(a);close(fd);
}
