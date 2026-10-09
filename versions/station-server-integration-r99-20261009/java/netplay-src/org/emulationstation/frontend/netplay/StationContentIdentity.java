package org.emulationstation.frontend.netplay;

import org.emulationstation.frontend.station.StationApi;
import java.io.*;
import java.nio.ByteBuffer;
import java.nio.charset.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.regex.*;

/** Exact CUE and track identity. Called only when preparing an online room. */
final class StationContentIdentity {
    private static final int MAX_CUE_BYTES=512*1024;
    private static final Pattern FILE=Pattern.compile("^\\s*FILE\\s+(?:\"([^\"\\r\\n]+)\"|([^\\s\"\\r\\n]+))\\s+\\S+\\s*$",Pattern.CASE_INSENSITIVE);
    private static final Pattern FILE_START=Pattern.compile("^\\s*FILE\\s+",Pattern.CASE_INSENSITIVE);
    private static final Comparator<String> UTF8_ORDER=(a,b)->{
        byte[] x=a.getBytes(StandardCharsets.UTF_8),y=b.getBytes(StandardCharsets.UTF_8);
        for(int i=0;i<Math.min(x.length,y.length);i++){int d=(x[i]&255)-(y[i]&255);if(d!=0)return d;}
        return x.length-y.length;
    };
    static String identity(File launch,StationApi.Cancellation cancel)throws Exception {
        return identity(launch,"",cancel);
    }
    static String identity(File launch,String scheme,StationApi.Cancellation cancel)throws Exception {
        if(scheme==null||scheme.isEmpty())return fileSha(launch,cancel);
        if("cue-set-v1".equals(scheme)&&launch.getName().toLowerCase(Locale.ROOT).endsWith(".cue"))return cue(launch,cancel);
        throw new IOException("Esta identidade de conteúdo ainda não é compatível com o motor online do aplicativo.");
    }
    static String fileSha(File file,StationApi.Cancellation cancel)throws Exception {
        if(!file.isFile()||Files.isSymbolicLink(file.toPath()))throw new IOException("O arquivo necessário não está instalado.");
        MessageDigest digest=MessageDigest.getInstance("SHA-256");byte[] block=new byte[131072];
        try(InputStream input=new FileInputStream(file)){int count;while((count=input.read(block))!=-1){cancel.check();digest.update(block,0,count);}}
        return hex(digest.digest());
    }
    private static String cue(File launch,StationApi.Cancellation cancel)throws Exception {
        if(!launch.isFile()||Files.isSymbolicLink(launch.toPath())||launch.length()>MAX_CUE_BYTES)throw new IOException("O arquivo CUE não está disponível.");
        byte[] raw;
        try(InputStream input=new FileInputStream(launch);ByteArrayOutputStream output=new ByteArrayOutputStream()){
            byte[] block=new byte[8192];int count;
            while((count=input.read(block))!=-1){cancel.check();if(output.size()+count>MAX_CUE_BYTES)throw new IOException("CUE fora do limite.");output.write(block,0,count);}raw=output.toByteArray();
        }
        String text=StandardCharsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(raw)).toString();
        if(text.startsWith("\uFEFF"))text=text.substring(1);
        SortedSet<String> names=new TreeSet<>(UTF8_ORDER);int references=0;
        for(String line:text.split("\\r\\n|\\n|\\r",-1)){
            if(!FILE_START.matcher(line).find())continue;
            Matcher match=FILE.matcher(line);if(!match.matches())throw new IOException("Referência CUE não reconhecida.");
            String name=match.group(1)!=null?match.group(1):match.group(2);safe(name);names.add(name);references++;
        }
        if(references==0)throw new IOException("O CUE não informa as faixas do jogo.");
        safe(launch.getName());names.add(launch.getName());
        File root=launch.getParentFile().getCanonicalFile();
        MessageDigest identity=MessageDigest.getInstance("SHA-256");
        update(identity,"TurboRamaStation/content-set/v1\nlaunch="+encoded(launch.getName())+"\n");
        for(String name:names){
            File file=root;
            for(String part:name.split("/")){file=new File(file,part);if(Files.isSymbolicLink(file.toPath()))throw new IOException("Faixa do jogo inválida.");}
            if(!file.isFile())throw new IOException("Uma faixa do jogo não está instalada.");
            long size=file.length(),time=file.lastModified();String sha=fileSha(file,cancel);
            if(file.length()!=size||file.lastModified()!=time)throw new IOException("O jogo mudou durante a preparação.");
            update(identity,encoded(name)+"\t"+size+"\t"+sha+"\n");
        }
        return hex(identity.digest());
    }
    private static void safe(String name)throws IOException {
        if(name==null||name.isEmpty()||name.length()>4096||name.startsWith("/")||name.indexOf('\\')>=0||name.indexOf(':')>=0)throw new IOException("Nome de faixa inválido.");
        for(int i=0;i<name.length();i++)if(name.charAt(i)<32)throw new IOException("Nome de faixa inválido.");
        for(String part:name.split("/",-1))if(part.isEmpty()||part.equals(".")||part.equals(".."))throw new IOException("Nome de faixa inválido.");
    }
    private static void update(MessageDigest digest,String text){digest.update(text.getBytes(StandardCharsets.UTF_8));}
    private static String encoded(String text){return Base64.getUrlEncoder().withoutPadding().encodeToString(text.getBytes(StandardCharsets.UTF_8));}
    private static String hex(byte[] data){char[] digits="0123456789abcdef".toCharArray(),result=new char[data.length*2];for(int i=0;i<data.length;i++){result[i*2]=digits[(data[i]&255)>>>4];result[i*2+1]=digits[data[i]&15];}return new String(result);}
}
