import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.*;
import javax.imageio.ImageIO;

/** Build utility: unpack the original emulator texture atlas with its source rectangles. */
public final class BuildControlSprites {
    public static void main(String[] args)throws Exception {
        File root=new File(args[0]),out=new File(root,"assets/station-online/overlays/station-local/img");
        for(String system:new String[]{"snes","megadrive"}){
            BufferedImage atlas=ImageIO.read(new File(root,"sprite-source/"+system+".png"));
            if(atlas.getWidth()!=256||atlas.getHeight()!=256)throw new IOException("Unexpected atlas size");
            sprite(atlas,out,system+"-dpad",0,0,4,4);
            sprite(atlas,out,system+"-a",4,0,2,2);sprite(atlas,out,system+"-b",6,0,2,2);
            if(system.equals("snes")){
                sprite(atlas,out,"snes-x",4,2,2,2);sprite(atlas,out,"snes-y",6,2,2,2);
                sprite(atlas,out,"snes-l",4,4,2,2);sprite(atlas,out,"snes-r",6,4,2,2);
                sprite(atlas,out,"snes-select",0,6,2,1);
            }else{
                sprite(atlas,out,"megadrive-c",4,2,2,2);sprite(atlas,out,"megadrive-x",6,2,2,2);
                sprite(atlas,out,"megadrive-y",0,4,2,2);sprite(atlas,out,"megadrive-z",2,4,2,2);
                sprite(atlas,out,"megadrive-mode",0,6,2,1);
            }
            sprite(atlas,out,system+"-start",0,7,2,1);
        }
        label(out,"three","3 / 6");label(out,"six","6 / 3");
    }
    static void sprite(BufferedImage src,File out,String name,int x,int y,int w,int h)throws Exception {
        ImageIO.write(src.getSubimage(x*32,y*32,w*32,h*32),"png",new File(out,name+".png"));
    }
    static void label(File out,String name,String text)throws Exception {
        BufferedImage image=new BufferedImage(128,60,BufferedImage.TYPE_INT_ARGB);Graphics2D g=image.createGraphics();
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING,RenderingHints.VALUE_ANTIALIAS_ON);
        g.setColor(new Color(0,0,0,100));g.fillRoundRect(1,1,126,58,24,24);
        g.setColor(Color.WHITE);g.setFont(new Font(Font.SANS_SERIF,Font.PLAIN,29));
        FontMetrics fm=g.getFontMetrics();g.drawString(text,(128-fm.stringWidth(text))/2,(60-fm.getHeight())/2+fm.getAscent());
        g.dispose();ImageIO.write(image,"png",new File(out,name+".png"));
    }
}
