import numpy as np
import cv2 as cv

# Load homography matrix
H = np.array([
    [ 4.158013,  5.076947, -1146.668632],
    [-1.674058,  8.920382, -450.058258],
    [-0.000171,  0.003455,  1.000000],
])

# Load images
src = cv.imread('snapshot.png', -1)
dst = cv.imread('referenceChessboard.png', -1)    

# Pixels Per Inch constant for coordinate conversion
PPI = 96.0


def process_point(x, y):
    """Process a selected point and calculate its transformed coordinates.
    
    Args:
        x, y: Source point coordinates
    """
    global src_copy, dst_copy
    
    # Mark point in source image
    cv.circle(src_copy, (x, y), 5, (0, 0, 255), -1)
    
    # Transform point to destination using homography
    src_point = np.array([[x, y]], dtype='float32')
    src_point = np.array([src_point])  # shape (1, 1, 2) for cv2.perspectiveTransform
    dst_point = cv.perspectiveTransform(src_point, H)

    # Get transformed coordinates
    dst_x, dst_y = int(dst_point[0][0][0]), int(dst_point[0][0][1])
    
    # Mark transformed point in destination image
    cv.circle(dst_copy, (dst_x, dst_y), 5, (0, 255, 0), -1)
    
    # Display the coordinates in console (convert pixels to inches)
    dst_x_inches = dst_x / PPI
    dst_y_inches = dst_y / PPI
    print(f"Source: ({x}, {y}) -> Destination: ({dst_x_inches:.2f}, {dst_y_inches:.2f}) inches")


def select_point_src(event, x, y, flags, param):
    """Mouse callback function for source image.
    
    Args:
        event: Mouse event type
        x, y: Mouse coordinates
        flags: Additional flags
        param: Additional parameters
    """
    if event == cv.EVENT_LBUTTONDOWN:
        process_point(x, y)


def chess(img):
    """Find chessboard corners in an image.
    
    Args:
        img: Input image with chessboard
        
    Returns:
        Array of detected corner coordinates
    """
    nline = 7
    ncol = 7
    
    # Termination criteria for corner refinement
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 1e-2000)

    # Convert to grayscale
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Find the chessboard corners
    ret, corners = cv.findChessboardCorners(gray, (nline, ncol), None)
    if not ret:
        print("Chessboard corners not found!")
        return []

    # Refine the corners
    corners = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
    
    return corners


# Create copies of images for drawing
src_copy = src.copy()
dst_copy = dst.copy()

# Create windows and set mouse callbacks
cv.namedWindow('src')
cv.setMouseCallback('src', select_point_src)
cv.namedWindow('dst')

print("Homography Test Tool")
print("Controls:")
print("  Left-click on source image: Transform point")
print("  c: Auto-detect and transform chessboard corners")
print("  ESC: Exit")

while True:
    cv.imshow('src', src_copy)
    cv.imshow('dst', dst_copy)
    
    k = cv.waitKey(1) & 0xFF
    if k == 27:  # Press 'ESC' to exit
        break
    elif k == ord('c'):
        print('Auto-detecting chessboard corners')
        corners = chess(src_copy)
        
        if len(corners) > 0:
            for pt in corners:
                src_x, src_y = pt[0]
                process_point(round(src_x), round(src_y))
        else:
            print("No chessboard corners detected")

cv.destroyAllWindows()
