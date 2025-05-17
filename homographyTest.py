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


# Mouse callback function for the source image
def select_point_src(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDOWN:
        process_point(x, y)
def process_point(x, y):
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
    
    # Display the coordinates in console
    dst_x /= 96
    dst_y /= 96
    print(f"Source: ({x}, {y}) -> Destination: ({dst_x}, {dst_y})")

def chess(img):
    nline = 7
    ncol = 7
    
    ## termination criteria
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 1000000000, 1e-2000)

    ## processing
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Find the chessboard corners
    ret, corners = cv.findChessboardCorners(gray, (nline, ncol), None)

    corners = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
    return corners


src_copy = src.copy()
dst_copy = dst.copy()

# Create windows and set mouse callbacks
cv.namedWindow('src')
cv.setMouseCallback('src', select_point_src)
cv.namedWindow('dst')

# Display images and handle key events

while True:
    cv.imshow('src', src_copy)
    cv.imshow('dst', dst_copy)
    
    k = cv.waitKey(1) & 0xFF
    if k == 27:  # Press 'ESC' to exit
        break
    elif k == ord('c'):
        print('auto chessboard')
        for pt in chess(src_copy):
            src_x, src_y = pt[0]
            process_point(round(src_x), round(src_y))


            process_point(209, 231)         

cv.destroyAllWindows()
