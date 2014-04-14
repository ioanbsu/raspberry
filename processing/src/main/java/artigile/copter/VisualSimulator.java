package artigile.copter;

import com.google.common.base.Charsets;
import com.google.common.base.Splitter;
import com.google.common.collect.Lists;
import com.google.common.io.CharStreams;
import com.google.common.io.Files;
import processing.core.PApplet;
import processing.opengl.PGraphics3D;
import sun.plugin2.message.Message;

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

    private List<CopterStateData> parsedData;
    private Iterator<CopterStateData> parsedDataIterator;
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

    private CopterStateData copterStateData = new CopterStateData(10, 5, 5, 0, 0, 0);


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
                parsedData.add(new CopterStateData(valuesList.next(), valuesList.next(), valuesList.next(), valuesList.next(),
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
        CopterStateData data = null;
        if (!parsedDataIterator.hasNext()) {
            parsedDataIterator = parsedData.iterator();
            frameCounter = 0;
        }

        if (System.currentTimeMillis() - lastChecked > 15000) {
            copterStateData.setRoll((float) Math.random());
            copterStateData.setPitch((float) Math.random());
            copterStateData.setYaw((float) Math.random());
            lastChecked = System.currentTimeMillis();
        }
        data =readFromServer();// copterStateData;//readFromServer();//   parsedDataIterator.next();//
        background(0);
        lights();

        pushMatrix();


        smoothedValueX += (data.getRoll() - smoothedValueX) / smoothingX;
        smoothedValueY += (data.getPitch() - smoothedValueY) / smoothingY;
        smoothedValueZ += (data.getYaw() - smoothedValueZ) / smoothingZ;

        rotateX(data.getRoll());
        rotateY(data.getPitch() * -1);
        rotateZ(data.getYaw());
//            translate(0, 0, 0);
        box(100);

        popMatrix();
        frameCounter++;

        stroke(255);
        line(0, 0, 0, 1000, 0, 0);
        line(0, 0, 0, 0, 1000, 0);
        line(0, 0, 0, 0, 0, 1000);

        textSize(40);
        rotateX(5.99F);
        rotateY(0.36F);
        rotateZ(4.35F);
        MotorSpeeds motorSpeeds = getMotorSpeeds(getDesiredTorques(data));
        text(MessageFormat.format("{0} - {1} - {2} - {3} ", motorSpeeds.getX1(), motorSpeeds.getX2(), motorSpeeds.getX3(), motorSpeeds.getX4()), 0, 300, 0);

        recalculatePosition(motorSpeeds);

    }

    private void recalculatePosition(MotorSpeeds motorSpeeds) {

        float db = 0.000001F;
        float k = 0.0000002F;
        Torques torques = new Torques(db * (motorSpeeds.getX2() * motorSpeeds.getX2() - motorSpeeds.getX4() * motorSpeeds.getX4()),
                db * (motorSpeeds.getX1() * motorSpeeds.getX1() - motorSpeeds.getX3() * motorSpeeds.getX3()),
                k * (motorSpeeds.getX1() * motorSpeeds.getX1() + motorSpeeds.getX3() * motorSpeeds.getX3() - motorSpeeds.getX2() * motorSpeeds.getX2() - motorSpeeds.getX4() * motorSpeeds.getX4()));
        float randomA = 0;//(float) (Math.random() / 100);
        float randomB = 0;//(float) (Math.random() / 100);
        float randomC = 0;//(float) (Math.random() / 100);
        copterStateData.setRoll(copterStateData.getRoll() + torques.getRoll() / 10 + randomA);
        copterStateData.setPitch(copterStateData.getPitch() + torques.getPitch() / 10 + randomB);
        copterStateData.setYaw(copterStateData.getYaw() + torques.getYaw() / 10 + randomC);

//        System.out.println(MessageFormat.format("{0},{1},{2}",torques.getRoll(),torques.getPitch(),torques.getYaw()));
    }

    private CopterStateData readFromServer() {
        HttpURLConnection connection = null;
        try {
            connection = (HttpURLConnection) new URL("http://192.168.1.31:3030").openConnection();
            String pageStringRepresentation = CharStreams.toString(new InputStreamReader(connection.getInputStream(), Charsets.UTF_8));
            System.out.println(pageStringRepresentation);
            Iterator<String> iterator = SPACE_SPLITTER.split(pageStringRepresentation).iterator();
            return new CopterStateData("0", "0", "0", "0", "0", "0", "0", iterator.next(), iterator.next(), iterator.next(),
                    "0", "0", "0", 0F);
        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
        return null;
    }

    private Torques getDesiredTorques(CopterStateData copterStateData) {
        final float G_MATRIX[] = new float[]{0.5F, 0.5F, .2F};
        int ALPHA_CONSTANT = 20;

        float roll = copterStateData.getPitch();
        float pitch = copterStateData.getRoll();
        float yaw = copterStateData.getYaw();
        float rollTorque = -1 * G_MATRIX[0] * copterStateData.getPitchSpeed() - ALPHA_CONSTANT * (
                sin(roll / 2) * cos(pitch / 2) * cos(yaw / 2) -
                        cos(roll / 2) * sin(pitch / 2) * sin(yaw / 2));
        float pitchTorque = -1 * G_MATRIX[0] * copterStateData.getRollSpeed() - ALPHA_CONSTANT * (
                cos(roll / 2) * sin(pitch / 2) * cos(yaw / 2) +
                        sin(roll / 2) * cos(pitch / 2) * sin(yaw / 2));
        float yawTorque = -1 * G_MATRIX[0] * copterStateData.getYawSpeed() - ALPHA_CONSTANT * (
                cos(roll / 2) * cos(pitch / 2) * sin(yaw / 2) -
                        sin(roll / 2) * sin(pitch / 2) * cos(yaw / 2));
        return new Torques(pitchTorque, rollTorque, yawTorque);

    }

    private MotorSpeeds getMotorSpeeds(Torques torques) {
        float a1 = 62690.9247649F;
        float a2 = 10000;
        float a3 = 8620.690F;
        int constantDesiredTorque = (int) (100 * a3);

        float t1 = torques.getRoll();
        float t2 = torques.getPitch();
        float t3 = torques.getYaw();
        float w1 = max(t2 * a1 + t3 * a2 + constantDesiredTorque, 0);
        float w2 = max(t1 * a1 - t3 * a2 + constantDesiredTorque, 0);
        float w3 = max(-t2 * a1 + t3 * a2 + constantDesiredTorque, 0);
        float w4 = max(-t1 * a1 - t3 * a2 + constantDesiredTorque, 0);

        return new MotorSpeeds((int) Math.sqrt(w1), (int) Math.sqrt(w2), (int) Math.sqrt(w3), (int) Math.sqrt(w4));
    }

    private static class CopterStateData {

        private int w1;
        private int w2;
        private int w3;
        private int w4;
        private float torqueX;
        private float torqueY;
        private float torqueZ;
        private float roll;
        private float pitch;
        private float yaw;
        private float pitchSpeed;
        private float rollSpeed;
        private float yawSpeed;

        private CopterStateData(String w1, String w2, String w3, String w4, String torqueX, String torqueY, String torqueZ, String roll,
                                String pitch, String yaw, String pitchSpeed, String rollSpeed, String yawSpeed, float i) {
            this.w1 = Integer.valueOf(w1.trim());
            this.w2 = Integer.valueOf(w2.trim());
            this.w3 = Integer.valueOf(w3.trim());
            this.w4 = Integer.valueOf(w4.trim());
            this.torqueX = Float.valueOf(torqueX.trim());
            this.torqueY = Float.valueOf(torqueY.trim());
            this.torqueZ = Float.valueOf(torqueZ.trim());
            this.roll = Float.valueOf(roll.trim()) * 2;
            this.pitch = Float.valueOf(pitch.trim()) * 2;
            this.yaw = Float.valueOf(yaw.trim()) * 2;
            this.pitchSpeed = Float.valueOf(pitchSpeed.trim());
            this.rollSpeed = Float.valueOf(rollSpeed.trim());
            this.yawSpeed = Float.valueOf(yawSpeed.trim());
        }

        private CopterStateData(float roll, float pitch, float yaw, float pitchSpeed, float rollSpeed, float yawSpeed) {
            this.roll = roll;
            this.pitch = pitch;
            this.yaw = yaw;
            this.pitchSpeed = pitchSpeed;
            this.rollSpeed = rollSpeed;
            this.yawSpeed = yawSpeed;
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

        public float getRoll() {
            return roll;
        }

        public float getPitch() {
            return pitch;
        }

        public float getYaw() {
            return yaw;
        }

        public float getPitchSpeed() {
            return pitchSpeed;
        }

        public float getRollSpeed() {
            return rollSpeed;
        }

        public float getYawSpeed() {
            return yawSpeed;
        }

        public void setRoll(float roll) {
            this.roll = roll;
        }

        public void setPitch(float pitch) {
            this.pitch = pitch;
        }

        public void setYaw(float yaw) {
            this.yaw = yaw;
        }
    }
}
