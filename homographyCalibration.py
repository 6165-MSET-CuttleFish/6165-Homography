import numpy as np
import cv2 as cv

# Global variables
drawing = False
src_x, src_y = -1, -1
dst_x, dst_y = -1, -1

src_list = []
dst_list = []

rotate = 0
flip = 0

# Rows, Cols of chessboard vertices, 7 for standard chessboard
chessboard = [7, 7]

# Load images
src = cv.imread('snapshot.png', -1)
dst = cv.imread('referenceChessboard.png', -1)


def select_points_src(event, x, y, flags, param):
    """Mouse callback function for source image.
    
    Args:
        event: Mouse event type
        x, y: Mouse coordinates
        flags: Additional flags
        param: Additional parameters
    """
    global src_x, src_y, drawing, src_copy
    
    if event == cv.EVENT_LBUTTONDOWN:
        drawing = True
        src_x, src_y = x, y
        cv.circle(src_copy, (x, y), 5, (0, 0, 255), -1)
    elif event == cv.EVENT_LBUTTONUP:
        drawing = False


def select_points_dst(event, x, y, flags, param):
    """Mouse callback function for destination image.
    
    Args:
        event: Mouse event type
        x, y: Mouse coordinates
        flags: Additional flags
        param: Additional parameters
    """
    global dst_x, dst_y, drawing, dst_copy
    
    if event == cv.EVENT_LBUTTONDOWN:
        drawing = True
        dst_x, dst_y = x, y
        cv.circle(dst_copy, (x, y), 5, (0, 0, 255), -1)
    elif event == cv.EVENT_LBUTTONUP:
        drawing = False


def get_plan_view(src, dst):
    """Calculate homography and warp source image to destination perspective.
    
    Args:
        src: Source image
        dst: Destination image
        
    Returns:
        Warped perspective image
    """
    src_pts = np.array(src_list).reshape(-1, 1, 2)
    dst_pts = np.array(dst_list).reshape(-1, 1, 2)
    H, mask = cv.findHomography(src_pts, dst_pts)
    
    # Print homography matrix in Python format
    print("Python: \nH = np.array([")
    for row in H:
        print("    [{: .6f}, {: .6f}, {: .6f}],".format(row[0], row[1], row[2]))
    print("])")

    # Print homography matrix in Java format
    print("Java: \ndouble[][] H = {")
    for i, row in enumerate(H):
        print("    {", end="")
        print(", ".join(f"{val:.6f}" for val in row), end="")
        print("}" + ("," if i < len(H) - 1 else ""))
    print("};")
    
    plan_view = cv.warpPerspective(src, H, (dst.shape[1], dst.shape[0]))
    return plan_view


def merge_views(src, dst):
    """Merge source warped image with destination image.
    
    Args:
        src: Source image
        dst: Destination image
        
    Returns:
        Merged image
    """
    plan_view = get_plan_view(src, dst)
    
    # Replace black pixels in warped image with pixels from destination
    for i in range(0, dst.shape[0]):
        for j in range(0, dst.shape[1]):
            if (plan_view.item(i, j, 0) == 0 and
                plan_view.item(i, j, 1) == 0 and
                plan_view.item(i, j, 2) == 0):
                plan_view.itemset((i, j, 0), dst.item(i, j, 0))
                plan_view.itemset((i, j, 1), dst.item(i, j, 1))
                plan_view.itemset((i, j, 2), dst.item(i, j, 2))
    
    return plan_view


def chess(img):
    """Find chessboard corners in an image.
    
    Args:
        img: Input image with chessboard
        
    Returns:
        Array of detected corner coordinates
    """
    nline = chessboard[0]  # Number of inner corners in the grid (rows)
    ncol = chessboard[1]   # Number of inner corners in the grid (columns)

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


def get_rainbow_color(index, total):
    """Generate a color smoothly transitioning from red to purple.
    
    Args:
        index: Current index
        total: Total number of elements
        
    Returns:
        BGR color tuple
    """
    start_hue, end_hue = 0, 140  # Hue range from red (0) to purple (140)
    hue = int(start_hue + (end_hue - start_hue) * index / (total - 1))
    color_hsv = np.uint8([[[hue, 255, 255]]])  # Full saturation & value
    color_bgr = cv.cvtColor(color_hsv, cv.COLOR_HSV2BGR)[0][0]
    
    return tuple(int(c) for c in color_bgr)


def apply_transformations(x, y, rotate, flip, size=768):
    """Apply rotation and flipping transformations to coordinates.
    
    Args:
        x, y: Input coordinates
        rotate: Rotation value (0-3 for 0°, 90°, 180°, 270°)
        flip: Flip value (0 for no flip, 1 for flip)
        size: Image size
        
    Returns:
        Transformed x, y coordinates
    """
    # Normalize rotation to 0, 90, 180, or 270
    rot = rotate % 4

    # Apply rotation
    if rot == 1:  # 90 degrees
        x, y = size - y, x
    elif rot == 2:  # 180 degrees
        x, y = size - x, size - y
    elif rot == 3:  # 270 degrees
        x, y = y, size - x

    # Apply flipping
    if flip % 2 == 1:  # Flip vertically
        y = size - y

    return x, y


def refresh_destination_points():
    """Refresh destination points after rotation/flip changes."""
    global dst_copy, dst_list
    
    dst_copy = dst.copy()
    dst_list = []
    
    dst_corners = chess(dst)
    if len(dst_corners) > 0:
        for i, pt in enumerate(dst_corners):
            dst_x, dst_y = pt[0]
            dst_x, dst_y = apply_transformations(dst_x, dst_y, rotate, flip)
            color = get_rainbow_color(i, chessboard[0] * chessboard[1])
            cv.circle(dst_copy, (int(dst_x), int(dst_y)), 6, color, -1)
            dst_list.append([dst_x, dst_y])


# Create copies of images for drawing
src_copy = src.copy()
cv.namedWindow('src')
cv.moveWindow("src", 80, 80)
cv.setMouseCallback('src', select_points_src)

dst_copy = dst.copy()
cv.namedWindow('dst')
cv.moveWindow("dst", 780, 80)
cv.setMouseCallback('dst', select_points_dst)

print("Controls:")
print("  s: Save current point pair")
print("  h: Create plan view with homography")
print("  m: Merge views")
print("  c: Auto-detect chessboard corners")
print("  r: Rotate destination image")
print("  f: Flip destination image")
print("  ESC: Exit")

while True:
    cv.imshow('src', src_copy)
    cv.imshow('dst', dst_copy)
    k = cv.waitKey(1) & 0xFF
    
    if k == ord('s'):
        print('Saving point pair')
        cv.circle(src_copy, (src_x, src_y), 5, (0, 255, 0), -1)
        cv.circle(dst_copy, (dst_x, dst_y), 5, (0, 255, 0), -1)
        src_list.append([src_x, src_y])
        dst_list.append([dst_x, dst_y])
        print("Source points:", src_list)
        print("Destination points:", dst_list)
        
    elif k == ord('h'):
        print('Creating plan view with homography')
        if len(src_list) >= 4 and len(dst_list) >= 4:
            plan_view = get_plan_view(src, dst)
            cv.imshow("Plan View", plan_view)
        else:
            print("Need at least 4 point pairs for homography")
            
    elif k == ord('m'):
        print('Merging views')
        if len(src_list) >= 4 and len(dst_list) >= 4:
            merge = merge_views(src, dst)
            cv.imshow("Merged View", merge)
        else:
            print("Need at least 4 point pairs for homography")
            
    elif k == ord('c'):
        print('Auto-detecting chessboard corners')
        src_list.clear()
        dst_list.clear()
        
        # Process source image
        src_corners = chess(src)
        if len(src_corners) > 0:
            src_copy = src.copy()  # Reset image
            for i, pt in enumerate(src_corners):
                src_x, src_y = pt[0]
                color = get_rainbow_color(i, chessboard[0] * chessboard[1])
                cv.circle(src_copy, (int(src_x), int(src_y)), 6, color, -1)
                src_list.append([src_x, src_y])
        
        # Process destination image
        dst_corners = chess(dst)
        if len(dst_corners) > 0:
            dst_copy = dst.copy()  # Reset image
            for i, pt in enumerate(dst_corners):
                dst_x, dst_y = pt[0]
                dst_x, dst_y = apply_transformations(dst_x, dst_y, rotate, flip)
                color = get_rainbow_color(i, chessboard[0] * chessboard[1])
                cv.circle(dst_copy, (int(dst_x), int(dst_y)), 6, color, -1)
                dst_list.append([dst_x, dst_y])
        
        print("Source points:", src_list)
        print("Destination points:", dst_list)
        
    elif k == ord('r'):
        rotate += 1
        print(f"Rotation: {rotate % 4} × 90°")
        refresh_destination_points()
        
    elif k == ord('f'):
        flip += 1
        print(f"Flip: {'On' if flip % 2 == 1 else 'Off'}")
        refresh_destination_points()
        
    elif k == 27:  # ESC key
        break

cv.destroyAllWindows()
