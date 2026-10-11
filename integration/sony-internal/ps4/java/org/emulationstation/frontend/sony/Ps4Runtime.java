package org.emulationstation.frontend.sony;

import org.json.JSONArray;
import org.json.JSONObject;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.security.MessageDigest;
import java.util.*;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/** Worker-only atomic extraction of the exact 397-file upstream runtime. */
final class Ps4Runtime {
    private Ps4Runtime() {}
    static File prepare(StationSonyAssets.Prepared module,File parent) throws Exception {
        File manifest=module.assetFile("runtime/manifest.json");
        JSONObject description=new JSONObject(new String(Files.readAllBytes(manifest.toPath()),StandardCharsets.UTF_8));
        String version=description.getString("runtimeVersion");
        if (description.getInt("schemaVersion")!=2 || description.getInt("protocolVersion")!=1 ||
            !version.equals("runtime-5b33842c8c7d")) throw new IOException("Versão PS4 incompatível");
        JSONArray rows=description.getJSONArray("files");
        if (rows.length()!=397) throw new IOException("Runtime PS4 incompleto");
        LinkedHashMap<String,JSONObject> wanted=new LinkedHashMap<>();
        for(int i=0;i<rows.length();i++) {
            JSONObject row=rows.getJSONObject(i); String name=row.getString("path");
            if (name.startsWith("/") || name.contains("\\") || Arrays.asList(name.split("/")).contains("..") ||
                name.isEmpty() || wanted.put(name,row)!=null) throw new IOException("Manifesto PS4 inválido");
        }
        if (!parent.isDirectory() && !parent.mkdirs()) throw new IOException("Sem pasta de runtime PS4");
        File target=new File(parent,version),marker=new File(target,".verified");
        String signature=hex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(manifest.toPath())));
        if(target.isDirectory() && marker.isFile() &&
           new String(Files.readAllBytes(marker.toPath()),StandardCharsets.US_ASCII).equals(signature)) {
            boolean complete=true;
            for(Map.Entry<String,JSONObject> e:wanted.entrySet()) {
                File f=confined(target,e.getKey());
                if(!f.isFile() || f.length()!=e.getValue().getLong("size") ||
                   !hashFile(f).equals(e.getValue().getString("sha256"))) {complete=false;break;}
                if(!f.setReadOnly())throw new IOException("Permissão inválida no runtime PS4");
            }
            if(complete) return target;
        }
        if(target.exists()) throw new IOException("Runtime PS4 local precisa ser reparado");
        File staging=new File(parent,".staging-"+UUID.randomUUID());
        if(!staging.mkdir()) throw new IOException("Sem espaço para preparar PS4");
        Set<String> seen=new HashSet<>();
        boolean promoted=false;
        try {
            try(ZipInputStream zip=new ZipInputStream(new BufferedInputStream(new FileInputStream(module.assetFile("runtime/runtime.zip"))))) {
                ZipEntry entry;
                byte[] buffer=new byte[65536];
                while((entry=zip.getNextEntry())!=null) {
                    String name=entry.getName();JSONObject row=wanted.get(name);
                    if(entry.isDirectory() || row==null || !seen.add(name)) throw new IOException("Arquivo inesperado no runtime PS4");
                    File file=confined(staging,name),directory=file.getParentFile();
                    if(!directory.isDirectory() && !directory.mkdirs()) throw new IOException("Sem espaço para preparar PS4");
                    long size=0,expected=row.getLong("size");MessageDigest digest=MessageDigest.getInstance("SHA-256");
                    try(FileOutputStream stream=new FileOutputStream(file)) {
                        int n;while((n=zip.read(buffer))!=-1) {
                            size+=n;if(size>expected) throw new IOException("Tamanho inválido no runtime PS4");
                            digest.update(buffer,0,n);stream.write(buffer,0,n);
                        }
                        stream.getFD().sync();
                    }
                    if(size!=expected || !hex(digest.digest()).equals(row.getString("sha256")))
                        throw new IOException("Hash inválido no runtime PS4");
                    if(!file.setExecutable(false,false)) throw new IOException("Permissão inválida no runtime PS4");
                    if(!file.setReadOnly()) throw new IOException("Permissão inválida no runtime PS4");
                    zip.closeEntry();
                }
            }
            if(seen.size()!=397) throw new IOException("Runtime PS4 incompleto");
            Files.write(new File(staging,".verified").toPath(),signature.getBytes(StandardCharsets.US_ASCII));
            Files.move(staging.toPath(),target.toPath(),StandardCopyOption.ATOMIC_MOVE);
            promoted=true;return target;
        } finally { if(!promoted) eraseStaging(staging); }
    }
    static File confined(File root,String relative) throws IOException {
        File file=new File(root,relative).getCanonicalFile();
        if(!file.toPath().startsWith(root.getCanonicalFile().toPath()) || file.equals(root.getCanonicalFile()))
            throw new IOException("Caminho PS4 inválido");
        return file;
    }
    static String hex(byte[] bytes) {
        StringBuilder result=new StringBuilder(bytes.length*2);
        for(byte b:bytes) result.append(String.format(Locale.ROOT,"%02x",b&255));return result.toString();
    }
    private static String hashFile(File file) throws Exception {
        MessageDigest digest=MessageDigest.getInstance("SHA-256");byte[] buffer=new byte[65536];
        try(InputStream input=new BufferedInputStream(new FileInputStream(file))) {
            int count;while((count=input.read(buffer))!=-1)digest.update(buffer,0,count);
        }return hex(digest.digest());
    }
    static void eraseStaging(File staging) throws IOException {
        // Called only with a private staging directory created by this operation.
        if(!staging.getName().startsWith(".staging-") || !staging.isDirectory()) return;
        try(java.util.stream.Stream<java.nio.file.Path> paths=Files.walk(staging.toPath())) {
            java.nio.file.Path[] values=paths.sorted(Comparator.reverseOrder()).toArray(java.nio.file.Path[]::new);
            for(java.nio.file.Path path:values) Files.deleteIfExists(path);
        }
    }
}
