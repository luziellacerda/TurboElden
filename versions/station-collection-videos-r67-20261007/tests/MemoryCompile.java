import java.io.*;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import javax.tools.*;

/** API34 type-check/bytecode compilation in memory. No DEX, APK or disk classes. */
class MemoryCompile {
    public static void main(String[] args) throws Exception {
        JavaCompiler compiler=ToolProvider.getSystemJavaCompiler();
        if(compiler==null)throw new IllegalStateException("Full JDK required");
        List<String> paths=new ArrayList<>();
        BufferedReader input=new BufferedReader(new InputStreamReader(System.in,StandardCharsets.UTF_8));
        for(String line;(line=input.readLine())!=null;)if(!line.isEmpty())paths.add(line);
        DiagnosticCollector<JavaFileObject> diagnostics=new DiagnosticCollector<>();
        try(StandardJavaFileManager standard=compiler.getStandardFileManager(diagnostics,null,StandardCharsets.UTF_8)){
            final int[] classes={0};final long[] bytes={0};
            final Map<String,byte[]> output=new HashMap<>();
            JavaFileManager memory=new ForwardingJavaFileManager<StandardJavaFileManager>(standard){
                @Override public JavaFileObject getJavaFileForOutput(Location location,String name,JavaFileObject.Kind kind,FileObject sibling){
                    return new SimpleJavaFileObject(URI.create("memory:///"+name.replace('.','/')+kind.extension),kind){
                        @Override public OutputStream openOutputStream(){return new ByteArrayOutputStream(){
                            @Override public void close()throws IOException{classes[0]++;bytes[0]+=size();output.put(name,toByteArray());super.close();}
                        };}
                    };
                }
            };
            boolean ok=compiler.getTask(null,memory,diagnostics,
                Arrays.asList("--release",args.length>1?"17":"8","-proc:none","-encoding","UTF-8","-classpath",args[0]),
                null,standard.getJavaFileObjectsFromStrings(paths)).call();
            for(Diagnostic<?> d:diagnostics.getDiagnostics())System.out.println(d.toString());
            System.out.println("success="+ok+" sources="+paths.size()+" classes="+classes[0]+" memoryBytes="+bytes[0]);
            if(!ok)System.exit(1);
            java.net.URLClassLoader libraries=new java.net.URLClassLoader(
                Arrays.stream(args[0].split(java.util.regex.Pattern.quote(File.pathSeparator)))
                    .map(p->{try{return new File(p).toURI().toURL();}catch(Exception e){throw new IllegalArgumentException(e);}})
                    .toArray(java.net.URL[]::new),ClassLoader.getPlatformClassLoader());
            ClassLoader loader=new ClassLoader(libraries){
                @Override protected Class<?> findClass(String name)throws ClassNotFoundException{
                    byte[] code=output.get(name);if(code==null)throw new ClassNotFoundException(name);
                    return defineClass(name,code,0,code.length);
                }
            };
            for(int i=1;i<args.length;i++){
                try{Class.forName(args[i],true,loader).getMethod("main",String[].class).invoke(null,(Object)new String[0]);}
                catch(java.lang.reflect.InvocationTargetException e){throw new RuntimeException(args[i],e.getCause());}
            }
            libraries.close();
        }
    }
}
