import numpy as np
import cv2 as cv

drawing = False
src_x, src_y = -1,-1
dst_x, dst_y = -1,-1

src_list = []
dst_list = []

rotate = 0
flip = 0

chessboard = [7, 7] # Rows, Col of chessboard verticies, 7 for standard chessboard


src = cv.imread('snapshot.png', -1)

dst = cv.imread('referenceChessboard.png', -1)



# mouse callback function
def select_points_src(event,x,y,flags,param):
    global src_x, src_y, drawing
    if event == cv.EVENT_LBUTTONDOWN:
        drawing = True
        src_x, src_y = x,y
        cv.circle(src_copy,(x,y),5,(0,0,255),-1)
    elif event == cv.EVENT_LBUTTONUP:
        drawing = False

# mouse callback function
def select_points_dst(event,x,y,flags,param):
    global dst_x, dst_y, drawing
    if event == cv.EVENT_LBUTTONDOWN:
        drawing = True
        dst_x, dst_y = x,y
        cv.circle(dst_copy,(x,y),5,(0,0,255),-1)
    elif event == cv.EVENT_LBUTTONUP:
        drawing = False

def get_plan_view(src, dst):
    src_pts = np.array(src_list).reshape(-1,1,2)
    dst_pts = np.array(dst_list).reshape(-1,1,2)
    H, mask = cv.findHomography(src_pts, dst_pts)
    
    print("Python: \nH = np.array([")
    for row in H:
        print("    [{: .6f}, {: .6f}, {: .6f}],".format(row[0], row[1], row[2]))
    print("])")

    print("Java: \ndouble[][] H = {")
    for i, row in enumerate(H):
        print("    {", end="")
        print(", ".join(f"{val:.6f}" for val in row), end="")
        print("}" + ("," if i < len(H) - 1 else ""))
    print("};")
    
    plan_view = cv.warpPerspective(src, H, (dst.shape[1], dst.shape[0]))
    return plan_view

def merge_views(src, dst):
    plan_view = get_plan_view(src, dst)
    for i in range(0,dst.shape[0]):
        for j in range(0, dst.shape[1]):
            if(plan_view.item(i,j,0) == 0 and \
               plan_view.item(i,j,1) == 0 and \
               plan_view.item(i,j,2) == 0):
                plan_view.itemset((i,j,0),dst.item(i,j,0))
                plan_view.itemset((i,j,1),dst.item(i,j,1))
                plan_view.itemset((i,j,2),dst.item(i,j,2))
    return plan_view;



def chess(img):
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

    # Reorder the corners to ensure correct orientation

    return corners

def get_rainbow_color(index, total):
    """Generate a color smoothly transitioning from red to purple."""
    start_hue, end_hue = 0, 140  # Hue range from red (0) to purple (160)
    hue = int(start_hue + (end_hue - start_hue) * index / (total - 1))  # Scale index within range
    color_hsv = np.uint8([[[hue, 255, 255]]])  # Full saturation & value for bright colors
    color_bgr = cv.cvtColor(color_hsv, cv.COLOR_HSV2BGR)[0][0]  # Convert HSV to BGR
    return tuple(int(c) for c in color_bgr)  # Convert to tuple for OpenCV

def apply_transformations(x, y, rotate, flip, size=768):
    """Apply rotation and flipping transformations based on the current values."""
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

src_copy = src.copy()
cv.namedWindow('src')
cv.moveWindow("src", 80,80);
cv.setMouseCallback('src', select_points_src)

dst_copy = dst.copy()
cv.namedWindow('dst')
cv.moveWindow("dst", 780,80);
cv.setMouseCallback('dst', select_points_dst)


while(1):
    cv.imshow('src',src_copy)
    cv.imshow('dst',dst_copy)
    k = cv.waitKey(1) & 0xFF
    if k == ord('s'):
        print('save points')
        cv.circle(src_copy,(src_x,src_y),5,(0,255,0),-1)
        cv.circle(dst_copy,(dst_x,dst_y),5,(0,255,0),-1)
        src_list.append([src_x,src_y])
        dst_list.append([dst_x,dst_y])
        print("src points:")
        print(src_list);
        print("dst points:")
        print(dst_list);
    elif k == ord('h'):
        print('create plan view')
        plan_view = get_plan_view(src, dst)
        cv.imshow("plan view", plan_view) 
    elif k == ord('m'):
        print('merge views')
        merge = merge_views(src,dst)      
        cv.imshow("merge", merge)
    elif k == ord('c'):
        print('auto chessboard')
        for i, pt in enumerate(chess(src_copy)):
            src_x, src_y = pt[0]
            color = get_rainbow_color(i, chessboard[0] * chessboard[1])
            cv.circle(src_copy, (int(src_x), int(src_y)), 6, color, -1)
            src_list.append([src_x, src_y])
        for i, pt in enumerate(chess(dst_copy)):
            dst_x, dst_y = pt[0]

            dst_x, dst_y = apply_transformations(dst_x, dst_y, rotate, flip)
            
            color = get_rainbow_color(i, chessboard[0] * chessboard[1])
            cv.circle(dst_copy, (int(dst_x), int(dst_y)), 6, color, -1)
            dst_list.append([dst_x,dst_y])
            
        print("src points:")
        print(src_list);
        print("dst points:")
        print(dst_list);
    elif k == ord('r'):
        rotate += 1
        print(rotate)
    elif k == ord('f'):
        flip += 1                      
        print(flip)
        
    elif k == 27:
        break

    if k == ord('r') or k == ord('f'):
        dst_copy = dst.copy()
        dst_list = []
        for i, pt in enumerate(chess(dst_copy)):
            dst_x, dst_y = pt[0]

            dst_x, dst_y = apply_transformations(dst_x, dst_y, rotate, flip)
            
            color = get_rainbow_color(i, 7*7)
            cv.circle(dst_copy, (int(dst_x), int(dst_y)), 6, color, -1)
            dst_list.append([dst_x,dst_y])
        
cv.destroyAllWindows()
