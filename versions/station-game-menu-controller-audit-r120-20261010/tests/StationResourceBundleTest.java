package org.emulationstation.frontend.station;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.Arrays;

public final class StationResourceBundleTest {
    private static int checks;
    private static void check(boolean value,String message){
        checks++;if(!value)throw new AssertionError(message);
    }
    private static StationBundledFiles.Source source(){
        return new StationBundledFiles.Source(){
            public String[] list(String path){
                return path.equals("resources")?new String[]{"font.bin","image.bin"}:new String[0];
            }
            public InputStream open(String path)throws IOException{
                if(path.equals("resources/font.bin"))return new ByteArrayInputStream(new byte[]{1,2,3});
                if(path.equals("resources/image.bin"))return new ByteArrayInputStream(new byte[]{4,5,6});
                throw new IOException("Missing fixture asset");
            }
        };
    }
    private static String marker(Path root)throws IOException{
        return new String(Files.readAllBytes(root.resolve(".installed-version")),StandardCharsets.UTF_8);
    }
    private static void writeMarker(Path root,String value)throws IOException{
        Files.createDirectories(root);
        Files.write(root.resolve(".installed-version"),value.getBytes(StandardCharsets.UTF_8));
    }
    private static void userFile(Path root)throws IOException{
        Files.write(root.resolve("user-added.cfg"),new byte[]{9,9});
    }
    private static void preserved(Path root)throws IOException{
        check(Arrays.equals(Files.readAllBytes(root.resolve("user-added.cfg")),new byte[]{9,9}),
            "User addition preserved");
    }
    public static void main(String[] args)throws Exception{
        Path fixture=Paths.get(args[0]).toAbsolutePath();
        Files.createDirectories(fixture);

        Path fresh=fixture.resolve("fresh");
        check(StationResourceBundle.install(source(),fresh)==2,"Fresh install copies complete bundle");
        check(marker(fresh).equals(StationResourceBundle.BUNDLE_ID),"Fresh marker uses stable bundle id");
        check(Files.size(fresh.resolve("font.bin"))==3&&Files.size(fresh.resolve("image.bin"))==3,
            "Fresh resources complete");

        Path current=fixture.resolve("current");
        writeMarker(current,StationResourceBundle.BUNDLE_ID);
        Files.write(current.resolve("font.bin"),new byte[]{42});
        Files.write(current.resolve("image.bin"),new byte[0]);
        userFile(current);
        check(StationResourceBundle.install(source(),current)==1,"Current bundle repairs only empty resource");
        check(Files.readAllBytes(current.resolve("font.bin"))[0]==42,"Current bundle preserves non-empty resource");
        check(Files.size(current.resolve("image.bin"))==3,"Current bundle restored empty resource");
        Files.delete(current.resolve("image.bin"));
        check(StationResourceBundle.install(source(),current)==1,"Current bundle restores missing resource");
        check(StationResourceBundle.install(source(),current)==0,"Current complete bundle performs no recopy");
        preserved(current);

        Path legacy=fixture.resolve("legacy");
        writeMarker(legacy,"1791662400000");
        Files.write(legacy.resolve("font.bin"),new byte[]{43});
        Files.write(legacy.resolve("image.bin"),new byte[]{44});
        userFile(legacy);
        check(StationResourceBundle.install(source(),legacy)==0,"Legacy numeric marker avoids full recopy");
        check(Files.readAllBytes(legacy.resolve("font.bin"))[0]==43&&
              Files.readAllBytes(legacy.resolve("image.bin"))[0]==44,
            "Legacy migration preserves non-empty resources");
        check(marker(legacy).equals(StationResourceBundle.BUNDLE_ID),"Legacy marker migrated");
        preserved(legacy);

        Path changed=fixture.resolve("changed");
        writeMarker(changed,"resources-sha256:previous-bundle");
        Files.write(changed.resolve("font.bin"),new byte[]{45});
        Files.write(changed.resolve("image.bin"),new byte[]{46});
        userFile(changed);
        check(StationResourceBundle.install(source(),changed)==2,"Changed bundle replaces packaged paths");
        check(Arrays.equals(Files.readAllBytes(changed.resolve("font.bin")),new byte[]{1,2,3})&&
              Arrays.equals(Files.readAllBytes(changed.resolve("image.bin")),new byte[]{4,5,6}),
            "Changed bundle installs new packaged bytes");
        check(marker(changed).equals(StationResourceBundle.BUNDLE_ID),"Changed bundle marker advanced");
        preserved(changed);

        check(StationResourceBundle.legacyTimestamp("1"),"Numeric legacy recognized");
        check(!StationResourceBundle.legacyTimestamp(StationResourceBundle.BUNDLE_ID),"Stable id is not legacy");
        check(!StationResourceBundle.legacyTimestamp(""),"Empty marker is not legacy");
        System.out.println("PASS "+checks+" resource bundle marker checks");
    }
}
