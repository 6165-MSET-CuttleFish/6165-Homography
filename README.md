# Homography
## What is homography?
Homography, put simply, is "some math to warp an image."

In our case, we want to take in an image from our camera and warp it onto the plane of the field so we can extract coordinates of objects in the real world. This allows us to take pixel coordinates on the image and convert them into real world coordinates.

More info on how homography works here: https://docs.opencv.org/4.x/d9/dab/tutorial_homography.html

## Our process:
There are really only two main steps:
1. Calculate the homography matrix.
2. Apply the matrix in real time to calculate locations of objects.

## Calculating the Homography Matrix
To calibrate/calculate your homography matrix, you need to make sure the camera is mounted on your robot in a way that it will move around or shift AT ALL, and you need a way to capture images.
You also need a chessboard, idealy one that is solid (flat, no creases, rigid) and with tiles 1 inch x 1 inch. You can print out an our ``referenceChessboard.png`` image on paper and maybe tape/glue it to cardboard, or multicolor 3dp our ``printedChessboard.3mf`` file.
We chose to 3dp ours.
If you cannot attain a chessboard with 1 in x 1 in tiles, you will just have to apply a scale to the calculated positions.
1. Place the chessboard fully within the camera's frame, near the middle. Make sure the front edge of the chessboard is parallel to the front edge of your robot.
2. Take a picture, download it.
3. Download ``homographyCalibration.py``, ``homographyTest.py``, and ``referenceChessboard.png`` and put them in the same directory as the image from your camera.
4. Change the filename on line 17 of ``homographyCalibration.py`` to match the name of the image from your camera.
5. Run the program (``python3 homographyCalibration.py``). If errors appear about missing packages, install them with pip (``pip3 install [packagename]``).
6. Press "c" on one of the image windows to have it automatically select all of the chessboard verticies. You can also manually do this by clicking a corresponding location on each image and pressing "s" for each pair.
7. The point dots are colored. Make the locations of the colored dots match between the two images by pressing "r" to rotate them and "f" to flip them.
8. Press "h" to calculate the homography matrix.
9. Copy if out of the terminal/shell output.

If you want to test the matrix, you can copy the python syntax for the matrix into ``homographyCalibration.py`` (line 6) and the image filename (line 13). Run that program, and test the matrix by clicking on a point on the chessboard on the snapshot. A dot at the corresponding location on the reference image should appear.

## Applying the matrix
You need to have a pipeline from which you can extract result coordinates. This sample code uses results from a Limelight pipeline, but you can adapt it to fit others.

1. Copy ``BasicHomographySample.java`` into your ``teamcode`` folder.
2. Copy the java syntax for the matrix into the ``BasicHomographySample.java`` on line 23. Change the active pipeline (line 61) if necessary.
3. Upload and run it. Detected results should be printed in Telemetry.
4. The printed coordinates of detected objects will likely be offset. We calibrate the offsets (``HORIZONTAL_OFFSET`` and ``VERTICAL_OFFSET``) by placing a detected object at a known position, for instance, 24 inches in front of the center of the robot, equivalent to the coordinate (0, 24). Modify the offsets to make the printed coordinate match the expected coordinate.
<br/>

<br/>

<br/>

Team 6165 MSET Cuttlefish
