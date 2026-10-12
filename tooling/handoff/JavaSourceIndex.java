import com.sun.source.tree.*;
import com.sun.source.util.*;
import javax.tools.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Syntax index only: parses source without resolving Android or emulator APIs. */
public class JavaSourceIndex {
  static String json(String s) {
    StringBuilder b=new StringBuilder("\"");
    for(char c:s.toCharArray()) switch(c) {
      case '\\':b.append("\\\\");break; case '"':b.append("\\\"");break;
      case '\n':b.append("\\n");break;case '\r':b.append("\\r");break;case '\t':b.append("\\t");break;
      default:if(c<32)b.append(String.format("\\u%04x",(int)c));else b.append(c);
    }
    return b.append('"').toString();
  }
  public static void main(String[] args) throws Exception {
    JavaCompiler compiler=ToolProvider.getSystemJavaCompiler();
    List<String> names=Files.readAllLines(Path.of(args[0]),StandardCharsets.UTF_8);
    DiagnosticCollector<JavaFileObject> diagnostics=new DiagnosticCollector<>();
    StringBuilder result=new StringBuilder("[");boolean[] first={true};
    try(StandardJavaFileManager fm=compiler.getStandardFileManager(diagnostics,null,StandardCharsets.UTF_8)) {
      JavacTask task=(JavacTask)compiler.getTask(null,fm,diagnostics,List.of("-proc:none"),null,fm.getJavaFileObjectsFromStrings(names));
      Trees trees=Trees.instance(task);
      for(CompilationUnitTree unit:task.parse()) {
        String file=Path.of(unit.getSourceFile().toUri()).toString();
        new TreePathScanner<Void,Void>() {
          Deque<String> owners=new ArrayDeque<>();
          public Void visitClass(ClassTree c,Void v) {
            owners.addLast(c.getSimpleName().toString().isEmpty()?"<anonymous>":c.getSimpleName().toString());
            super.visitClass(c,v);owners.removeLast();return null;
          }
          public Void visitMethod(MethodTree m,Void v) {
            long start=trees.getSourcePositions().getStartPosition(unit,m),end=trees.getSourcePositions().getEndPosition(unit,m);
            String name=m.getName().toString();
            String signature=m.getModifiers()+" "+(m.getReturnType()==null?"":m.getReturnType()+" ")+name+"("+m.getParameters()+")";
            if(!first[0])result.append(',');first[0]=false;
            result.append("{\"file\":").append(json(file)).append(",\"owner\":").append(json(String.join(".",owners)))
              .append(",\"name\":").append(json(name)).append(",\"signature\":").append(json(signature.trim()))
              .append(",\"line\":").append(unit.getLineMap().getLineNumber(start)).append(",\"endLine\":").append(unit.getLineMap().getLineNumber(Math.max(start,end-1)))
              .append(",\"nativeDeclaration\":").append(m.getModifiers().getFlags().contains(javax.lang.model.element.Modifier.NATIVE)).append('}');
            return super.visitMethod(m,v);
          }
        }.scan(unit,null);
      }
    }
    for(Diagnostic<?> d:diagnostics.getDiagnostics()) if(d.getKind()==Diagnostic.Kind.ERROR)throw new IllegalArgumentException(d.toString());
    Files.writeString(Path.of(args[1]),result.append(']').toString(),StandardCharsets.UTF_8);
  }
}
