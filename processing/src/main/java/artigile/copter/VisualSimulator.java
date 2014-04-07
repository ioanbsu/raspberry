package artigile.copter;

import com.google.common.base.Charsets;
import com.google.common.base.Splitter;
import com.google.common.collect.Lists;
import com.google.common.io.CharStreams;
import com.google.common.io.Files;
import processing.core.PApplet;
import processing.opengl.PGraphics3D;

import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.charset.Charset;
import java.text.MessageFormat;
import java.util.Iterator;
import java.util.List;

/**
 * @author ivanbahdanau
 */
public class VisualSimulator extends PApplet {

    private List<CsvData> parsedData;
    private Iterator<CsvData> parsedDataIterator;
    public static final Splitter COMMA_SPLITTER = Splitter.on(",");
    public static final Splitter SPACE_SPLITTER = Splitter.on(" ");
    private long lastChecked = 0;
    private int frameCounter = 0;

    private float smoothedValueX = 0F;
    private float smoothedValueY = 0F;
    private float smoothedValueZ = 0F;

    public static final float initXAngle = 5.4F;
    public static final float initYAngle = 4.9F;
    public static final float initZAngle = 5.98F;
    public static final float smoothingX = 10F;
    public static final float smoothingY = 10F;
    public static final float smoothingZ = 10F;

    public static void main(String args[]) {
        PApplet.main(new String[]{"--present", "artigile.copter.VisualSimulator"});
    }

    public void setup() {
        size(1200, 850, PGraphics3D.P3D);
        camera(300, 300, 400, 0, 0, 0, 1, 1, 1);
        try {
            List<String> rawData = Files.readLines(new File("/Users/ivanbahdanau/Downloads/flyingCopterApr3.csv"), Charset.defaultCharset());
            parsedData = Lists.newArrayList();
            float i = 0F;
            for (String line : rawData) {
                if (line.contains("Running")) {
                    continue;
                }
                Iterator<String> valuesList = COMMA_SPLITTER.split(line).iterator();
                parsedData.add(new CsvData(valuesList.next(), valuesList.next(), valuesList.next(), valuesList.next(),
                        valuesList.next(), valuesList.next(), valuesList.next(),
                        valuesList.next(), valuesList.next(), valuesList.next(),
                        valuesList.next(), valuesList.next(), valuesList.next(), i));
//                i += 0.01;

            }
            parsedDataIterator = parsedData.iterator();
        } catch (IOException e) {
            e.printStackTrace();
        }


    }

    public void draw() {
        CsvData data = null;
        if (!parsedDataIterator.hasNext()) {
            parsedDataIterator = parsedData.iterator();
            frameCounter = 0;
        }
        if (System.currentTimeMillis() - lastChecked > 10) {
            data = readFromServer();// parsedDataIterator.next();//
            background(0);
            lights();

            pushMatrix();


            smoothedValueX += (data.getRotX() - smoothedValueX) / smoothingX;
            smoothedValueY += (data.getRotY() - smoothedValueY) / smoothingY;
            smoothedValueZ += (data.getRotZ() - smoothedValueZ) / smoothingZ;

            rotateX(data.getRotX());
            rotateY(data.getRotY() * -1);
            rotateZ(data.getRotZ());
//            translate(0, 0, 0);
            box(100);

            popMatrix();
            lastChecked = System.currentTimeMillis();
            frameCounter++;

            stroke(255);
            line(0, 0, 0, 1000, 0, 0);
            line(0, 0, 0, 0, 1000, 0);
            line(0, 0, 0, 0, 0, 1000);

            textSize(40);
            rotateX(5.99F);
            rotateY(0.36F);
            rotateZ(4.35F);
            text(MessageFormat.format("{0} - {1} - {2} - {3} ", frameCounter, mouseX, mouseY, smoothedValueY), 0, 300, 0);
//            rotateAngle+=0.01;
//            println(MessageFormat.format("{0},{1},{2}", mouseX, mouseY, smoothedValueZ));

        }

    }

    private CsvData readFromServer() {
        HttpURLConnection connection = null;
        try {
            connection = (HttpURLConnection) new URL("http://192.168.1.31:3030").openConnection();
            String pageStringRepresentation = CharStreams.toString(new InputStreamReader(connection.getInputStream(), Charsets.UTF_8));
            System.out.println(pageStringRepresentation);
            Iterator<String> iterator = SPACE_SPLITTER.split(pageStringRepresentation).iterator();
            return new CsvData("0", "0", "0", "0", "0", "0", "0", iterator.next(), iterator.next(), iterator.next(),
                    "0", "0", "0", 0F);
        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
        return null;
    }

    private static class CsvData {

        private int w1;
        private int w2;
        private int w3;
        private int w4;
        private float torqueX;
        private float torqueY;
        private float torqueZ;
        private float rotX;
        private float rotY;
        private float rotZ;
        private float speedX;
        private float speedY;
        private float speedZ;

        private CsvData(String w1, String w2, String w3, String w4, String torqueX, String torqueY, String torqueZ, String rotX,
                        String rotY, String rotZ, String speedX, String speedY, String speedZ, float i) {
            this.w1 = Integer.valueOf(w1.trim());
            this.w2 = Integer.valueOf(w2.trim());
            this.w3 = Integer.valueOf(w3.trim());
            this.w4 = Integer.valueOf(w4.trim());
            this.torqueX = Float.valueOf(torqueX.trim());
            this.torqueY = Float.valueOf(torqueY.trim());
            this.torqueZ = Float.valueOf(torqueZ.trim());
            this.rotX = Float.valueOf(rotX.trim()) * 2;
            this.rotY = Float.valueOf(rotY.trim()) * 2;
            this.rotZ = Float.valueOf(rotZ.trim()) * 2;
            this.speedX = Float.valueOf(speedX.trim());
            this.speedY = Float.valueOf(speedY.trim());
            this.speedZ = Float.valueOf(speedZ.trim());
        }

        public int getW1() {
            return w1;
        }

        public int getW2() {
            return w2;
        }

        public int getW3() {
            return w3;
        }

        public int getW4() {
            return w4;
        }

        public float getTorqueX() {
            return torqueX;
        }

        public float getTorqueY() {
            return torqueY;
        }

        public float getTorqueZ() {
            return torqueZ;
        }

        public float getRotX() {
            return rotX;
        }

        public float getRotY() {
            return rotY;
        }

        public float getRotZ() {
            return rotZ;
        }

        public float getSpeedX() {
            return speedX;
        }

        public float getSpeedY() {
            return speedY;
        }

        public float getSpeedZ() {
            return speedZ;
        }
    }
}
