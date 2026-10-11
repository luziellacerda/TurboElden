package org.emulationstation.frontend.sony;

import android.content.Context;
import android.net.Uri;
import android.os.ParcelFileDescriptor;
import android.os.StatFs;
import android.system.Os;
import android.system.StructStat;
import java.io.*;
import java.lang.reflect.InvocationTargetException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.security.MessageDigest;
import java.util.*;
import java.util.function.BiConsumer;
import org.json.JSONObject;

/** Automatic, private PKG registration using the actual upstream importer and SFO metadata. */
final class Ps4Game {
    final File root;final String titleId,title;
    private Ps4Game(File root,String titleId,String title) {this.root=root;this.titleId=titleId;this.title=title;}
    static Ps4Game prepare(Context context,Uri uri,File games,Class<?> entry,BiConsumer<Long,Long> progress) throws Exception {
        if(uri==null||!"content".equals(uri.getScheme()))throw new IOException("Escolha um pacote PS4 válido");
        if(!games.isDirectory()&&!games.mkdirs())throw new IOException("Não foi possível preparar a pasta PS4");
        try(ParcelFileDescriptor fd=context.getContentResolver().openFileDescriptor(uri,"r")) {
            if(fd==null)throw new IOException("O jogo PS4 não pôde ser aberto");
            StructStat stat=Os.fstat(fd.getFileDescriptor());
            if(stat.st_size<=0)throw new IOException("O pacote PS4 está vazio ou não pode ser lido");
            String[] probe=(String[])invoke(entry,"probe",new Class<?>[]{int.class},fd.getFd());
            if(probe.length!=6||!"OK".equals(probe[2]))throw status(probe.length>2?probe[2]:"ERROR");
            String fingerprint=Ps4Runtime.hex(MessageDigest.getInstance("SHA-256").digest(
                (uri.toString()+"\n"+stat.st_dev+"\n"+stat.st_ino+"\n"+stat.st_size+"\n"+stat.st_mtime+"\n"+stat.st_ctime+"\n"+probe[0])
                    .getBytes(StandardCharsets.UTF_8)));
            File target=Ps4Runtime.confined(games,fingerprint),marker=new File(target,".station-pkg.json");
            if(marker.isFile()) {
                JSONObject prior=new JSONObject(new String(Files.readAllBytes(marker.toPath()),StandardCharsets.UTF_8));
                if(fingerprint.equals(prior.optString("fingerprint")))return validate(target);
            }
            if(target.exists())throw new IOException("A importação local deste pacote está incompleta");
            long expanded=Long.parseLong(probe[4]);
            if(expanded<0||expanded>new StatFs(games.getAbsolutePath()).getAvailableBytes()-64L*1024*1024)
                throw new IOException("Sem espaço para preparar este jogo de PS4");
            File staging=new File(games,".staging-"+UUID.randomUUID());
            if(!staging.mkdir())throw new IOException("Sem espaço para preparar este jogo de PS4");
            boolean promoted=false;
            try {
                // Probe may have advanced the shared descriptor: restore it before extraction.
                Os.lseek(fd.getFileDescriptor(),0,android.system.OsConstants.SEEK_SET);
                String[] result=(String[])invoke(entry,"extract",new Class<?>[]{int.class,String.class,BiConsumer.class},
                    fd.getFd(),staging.getCanonicalPath(),progress);
                if(result.length!=3||!"OK".equals(result[0]))throw status(result.length>0?result[0]:"ERROR");
                Ps4Game game=validate(staging);
                JSONObject registration=new JSONObject().put("schemaVersion",1).put("fingerprint",fingerprint)
                    .put("titleId",game.titleId).put("contentId",probe[0]).put("packageBytes",stat.st_size);
                Files.write(new File(staging,".station-pkg.json").toPath(),registration.toString().getBytes(StandardCharsets.UTF_8));
                Files.move(staging.toPath(),target.toPath(),StandardCopyOption.ATOMIC_MOVE);
                promoted=true;return new Ps4Game(target,game.titleId,game.title);
            } finally {if(!promoted)Ps4Runtime.eraseStaging(staging);}
        }
    }
    static Object invoke(Class<?> entry,String method,Class<?>[] types,Object... arguments) throws Exception {
        try{return entry.getMethod(method,types).invoke(null,arguments);}
        catch(InvocationTargetException cause) {
            Throwable failure=cause.getCause();if(failure instanceof Exception)throw (Exception)failure;
            if(failure instanceof Error)throw (Error)failure;throw new IOException("Falha no motor PS4",failure);
        }
    }
    private static IOException status(String state) {
        if("NEED_PASSCODE".equals(state))return new IOException("Este pacote requer uma chave própria e não pode ser aberto automaticamente");
        if("CANCELLED".equals(state))return new IOException("Preparação do jogo cancelada");
        return new IOException("O pacote PS4 não pôde ser importado pelo motor");
    }
    static Ps4Game validate(File root) throws Exception {
        File eboot=Ps4Runtime.confined(root,"eboot.bin"),sfo=Ps4Runtime.confined(root,"sce_sys/param.sfo");
        if(!eboot.isFile()||eboot.length()==0||!eboot.canRead())throw new IOException("O pacote não contém um jogo completo de PS4");
        Map<String,String> metadata=sfo(sfo);String id=metadata.get("TITLE_ID");
        if(id==null||!id.matches("[A-Z]{4}[0-9]{5}"))throw new IOException("Identificador PS4 inválido no jogo");
        String title=metadata.get("TITLE");if(title==null||title.trim().isEmpty())title=id;
        return new Ps4Game(root.getCanonicalFile(),id,title);
    }
    static Map<String,String> sfo(File file) throws IOException {
        if(!file.isFile()||file.length()<20||file.length()>1024*1024)throw new IOException("Metadados PS4 ausentes");
        byte[] bytes=Files.readAllBytes(file.toPath());ByteBuffer data=ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN);
        if(data.getInt()!=0x46535000)throw new IOException("Metadados PS4 inválidos");
        data.getInt();int keys=data.getInt(),values=data.getInt(),count=data.getInt();
        if(count<1||count>4096||20L+count*16L>bytes.length||keys<20+count*16||values<keys||values>bytes.length)
            throw new IOException("Tabela PS4 inválida");
        Map<String,String> result=new HashMap<>();
        for(int i=0;i<count;i++) {
            int offset=20+i*16,keyOffset=Short.toUnsignedInt(data.getShort(offset)),format=Short.toUnsignedInt(data.getShort(offset+2));
            int length=data.getInt(offset+4),maximum=data.getInt(offset+8),valueOffset=data.getInt(offset+12);
            long keyStart=(long)keys+keyOffset,valueStart=(long)values+valueOffset;
            if(keyStart>=values||length<0||maximum<length||valueOffset<0||valueStart+length>bytes.length)
                throw new IOException("Entrada PS4 inválida");
            int keyEnd=(int)keyStart;while(keyEnd<values&&bytes[keyEnd]!=0)keyEnd++;
            if(keyEnd==values)throw new IOException("Nome PS4 inválido");
            String key=new String(bytes,(int)keyStart,keyEnd-(int)keyStart,StandardCharsets.UTF_8);
            if(format==0x0204) {
                int n=length;while(n>0&&bytes[(int)valueStart+n-1]==0)n--;
                String value=new String(bytes,(int)valueStart,n,StandardCharsets.UTF_8);
                if(result.put(key,value)!=null)throw new IOException("Metadados PS4 duplicados");
            }
        }return result;
    }
}
