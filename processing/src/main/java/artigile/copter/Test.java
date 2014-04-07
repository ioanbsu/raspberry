package artigile.copter;

import processing.core.PApplet;
import processing.opengl.PGraphics3D;

/**
 * @author ivanbahdanau
 */
public class Test extends PApplet {

    public static void main(String args[]) {
        PApplet.main(new String[]{"--present", "artigile.copter.Test"});
    }

    public void setup() {
        size(1200, 850, PGraphics3D.P3D);
        camera(300, 300, 400, 0, 0, 0, 1, 1, 1);
        line(0, 0, 0, 1000, 0, 0);
        line(0, 0, 0, 0, 1000, 0);
        line(0, 0, 0, 0, 0, 1000);
    }


    public void draw() {
        lights();
        background(0);

        pushMatrix();
        rotateY(radians(mouseY));
        rotateZ(radians(mouseX));
//            translate(0, 0, 0);
        box(100);
        popMatrix();

    }

}
