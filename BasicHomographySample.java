package org.firstinspires.ftc.robotcontroller.internal;

import java.util.ArrayList;
import java.util.List;

import com.qualcomm.hardware.limelightvision.LLResult;
import com.qualcomm.hardware.limelightvision.LLResultTypes;
import com.qualcomm.hardware.limelightvision.Limelight3A;
import com.qualcomm.robotcore.eventloop.opmode.Disabled;
import com.qualcomm.robotcore.eventloop.opmode.LinearOpMode;
import com.qualcomm.robotcore.eventloop.opmode.TeleOp;
import org.opencv.core.Point;


@TeleOp(name = "Concept: AprilTag", group="Linear OpMode")
public class BasicHomographySample extends LinearOpMode{

    // Offset constants, inches
    public static double HORIZONTAL_OFFSET = 0;
    public static double VERTICAL_OFFSET = 24;

    // Homography matrix
    private final double[][] H = {
            {4.158013, 5.076947, -1146.668632},
            {-1.674058, 8.920382, -450.058258},
            {-0.000171, 0.003455, 1.000000}
    };

    // Pixels Per Inch on Calibration Image
    private final double PPI = 96.0;

    private Limelight3A limelight;

    @Override
    public void runOpMode() {

        initializeLimelight();

        waitForStart();

        if (opModeIsActive()) {
            while (opModeIsActive()) {
                ArrayList<Item> results = processLimelightResults();

                StringBuilder output = new StringBuilder();

                for (Item r : results) {
                    output.append(r.toString()).append("\n");
                }

                telemetry.addData("Results", output.toString());
            }
        }
    }

    /**
     * Configures and starts the Limelight camera.
     */
    private void initializeLimelight() {
        limelight = hardwareMap.get(Limelight3A.class, "limelight");
        limelight.pipelineSwitch(0);
        limelight.start();
    }

    /**
     * Processes the latest results from the Limelight camera.
     */
    private ArrayList<Item> processLimelightResults() {
        LLResult results = limelight.getLatestResult();

        ArrayList<Item> items = new ArrayList<>();

        if (results != null && results.isValid()) {
            List<LLResultTypes.DetectorResult> detectorResults = results.getDetectorResults();

            for (LLResultTypes.DetectorResult result : detectorResults) {
                Point robotCoordinates = calculateRobotCoordinates(result);
                int id = result.getClassId();

                items.add(new Item(id, robotCoordinates));
            }
        }
        return items;
    }

    /**
     * Transforms detector result using homography matrix to get robot-relative coordinates.
     * @param result The detector result to transform
     * @return Robot-relative coordinates of the detected object
     */
    private Point calculateRobotCoordinates(LLResultTypes.DetectorResult result) {
        // Get pixel
        double x = result.getTargetXDegrees();
        double y = result.getTargetYDegrees();

        // Apply homography transformation
        double X_prime = H[0][0] * x + H[0][1] * y + H[0][2];
        double Y_prime = H[1][0] * x + H[1][1] * y + H[1][2];
        double W = H[2][0] * x + H[2][1] * y + H[2][2];
        double x_robot = X_prime / W / PPI + HORIZONTAL_OFFSET;
        double y_robot = Y_prime / W / PPI + VERTICAL_OFFSET;

        return new Point(x_robot, y_robot);
    }
}

/**
 * Helper class to store results after transformation.
 */
class Item {
    // Detected Class ID
    private int id;

    // Position
    private Point pos;

    public Item(int id, Point pos) {
        this.id = id;
        this.pos = pos;
    }

    public String toString() {
        return "Detected Item " + id + " at " + pos.toString();
    }
}
