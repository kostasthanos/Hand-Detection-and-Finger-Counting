#==================================#
# Hand Detection & Finger Counting #
#            with OpenCV           #
#----------------------------------#
#        Konstantinos Thanos       #
#        Mathematician, MSc        #
#               2020               #
#==================================#

# Import packages
import numpy as np
import math
import cv2

# Text settings
font = cv2.FONT_HERSHEY_PLAIN
text_color = (255,255,255)

# Video Capture
cap = cv2.VideoCapture(1)

# Define the Region Of Interest (ROI) window 
# Only inside this window the results will be visible
top_left = (245,50)
bottom_right = (580,295)

while True:
    _, frame = cap.read()
    # Horizontal flip (check if needed)
    frame = cv2.flip(frame, 1)
    # Frame shape : height and width
    h, w = frame.shape[:2] # h, w = 480, 640

    # "Paint" (background) with black color this area of the frame
    frame[0: 40, w-200: w] = (0) # Rectangle : (440,0) -> (640,40)
    # Add text on screen inside the above black area
    cv2.putText(frame, "Fingers : ", (w-190, 30), font, 2, text_color, 2) 
    
    # Draw a rectangle (yellow color) around ROI
    cv2.rectangle(frame, (top_left[0]-5, top_left[1]-5), (bottom_right[0]+5, bottom_right[1]+5), (0,255,255), 3)

    # ROI window for the tests (test_window)
    # Only inside this window the results will be visible
    test_window = frame[top_left[1]: bottom_right[1], top_left[0]: bottom_right[0]]

    # Apply Gaussian Blur
    test_window_blurred = cv2.GaussianBlur(test_window, (5,5), 0)
    
    # Transform to HSV format
    hsv = cv2.cvtColor(test_window_blurred, cv2.COLOR_BGR2HSV)

    # Create a range for the colors (skin color based on room light, may need to change)
    lower_color = np.array([0, 24, 0])
    upper_color = np.array([179,255,255])

    # Create a mask
    mask = cv2.inRange(hsv, lower_color, upper_color)
    cv2.imshow("Mask", mask) # Show mask frame

    # Find contours inside the ROI
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    if len(contours) > 0:
        # Find the maximum contour each time (on each frame)
        # --Max Contour--
        max_contour = max(contours, key = cv2.contourArea)
        # Draw maximum contour (blue color)
        cv2.drawContours(test_window, max_contour, -1, (255,0,0), 3)
        # Find the convex hull "around" the max_contour
        # --Convex Hull--
        convhull = cv2.convexHull(max_contour, returnPoints = True) 
        # Draw convex hull (red color)
        cv2.drawContours(test_window, [convhull], -1, (0,0,255), 3, 2)

        # Find the minimum y-value of the convexhull
        min_y = h # Set the minimum y-value equal to frame's height value
        final_point = (w, h)
        for i in range(len(convhull)):
            point = (convhull[i][0][0], convhull[i][0][1])
            if point[1] < min_y:
                min_y = point[1]
                final_point = point
        # Draw a circle (black color) to the point with the minimum y-value
        cv2.circle(test_window, final_point, 5, (0), 2)
    
        M = cv2.moments(max_contour) # Moments
        # Find the center of the max contour
        if M["m00"]!=0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            # Draw circle (red color) in the center of max contour
            cv2.circle(test_window, (cX, cY), 6, (0,0,255), 3)
            
        # Find the polygon with "extreme" points the points of the convex hull
        # --Contour Polygon--
        contour_poly = cv2.approxPolyDP(max_contour, 0.01*cv2.arcLength(max_contour,True), True)
        # Draw contour polygon (white color)
        #cv2.fillPoly(test_window, [max_contour], text_color) 

        hull = cv2.convexHull(contour_poly, returnPoints = False) # --Hull--

        # Find Defect points
        defects = cv2.convexityDefects(contour_poly, hull)
        if defects is not None:
            count = 0
            points = []
            for i in range(defects.shape[0]): # Len of arrays
                start_index, end_index, far_pt_index, fix_dept = defects[i][0]
                start_pts = tuple(contour_poly[start_index][0])
                end_pts = tuple(contour_poly[end_index][0])
                mid_pts = (int((start_pts[0]+end_pts[0])/2), int((start_pts[1]+end_pts[1])/2))
                far_pts = tuple(contour_poly[far_pt_index][0])
                
                points.append(mid_pts)
                # Draw circle (yellow color in the mid_pts defect points)
# ! #                cv2.circle(test_window, mid_pts, 2, (0,255,255), 2) 
                
                #--Start Points-- (yellow color)
# ! #                 cv2.circle(test_window, start_pts, 2, (0,255,255), 2)
                
                #--End Points-- (black color)
# ! #                 cv2.circle(test_window, end_pts, 2, (0), 2)
                
                #--Far Points-- (white color)
# ! #                 cv2.circle(test_window, far_pts, 2, text_color, 2)

                # Connect points with lines
                cv2.line(test_window, start_pts, end_pts, (0,255,0), 2)   # Connect with line start_pts and end_pts
                cv2.line(test_window, start_pts, far_pts, (0,255,255), 2) # Connect with line start_pts and far_pts
                cv2.line(test_window, end_pts, far_pts, text_color, 2)    # Connect with line end_pts and far_pts

                # --Calculate distances--
                # If p1 = (x1, y1) and p2 = (x2, y2) the the distance between them is
                # Dist : sqrt[(x2-x1)^2 + (y2-y1)^2]
                
                # Distance between the start and the end defect point
                a = np.sqrt((end_pts[0] - start_pts[0])**2 + (end_pts[1] - start_pts[1])**2)
                # Distance between the farthest point and the start point
                b = math.sqrt((far_pts[0] - start_pts[0])**2 + (far_pts[1] - start_pts[1])**2)
                # Distance between the farthest point and the end point
                c = math.sqrt((end_pts[0] - far_pts[0])**2 + (end_pts[1] - far_pts[1])**2)
                
                angle = math.acos((b**2 + c**2 - a**2) / (2*b*c))  # Find each angle

                # If angle > 90 then the farthest point is "outside the area of fingers"
                if angle <= np.pi/2:  
                    count += 1
# ! #                    cv2.circle(test_window, far_pts, 3, (0,255,255), -1)
                    frame[0:40, w-40:w] = (0)
                    for c in range(5):
                        if count == c:
                            cv2.putText(frame, str(count+1), (w-35,30), font, 2, text_color, 2)
                if len(points) <= 1 :
                    frame[0:40, w-40:w] = (0)
                    cv2.putText(frame, "1", (w-35,30), font, 2, text_color, 2)

  
    cv2.imshow("Frame", frame)
    
    key = cv2.waitKey(25)
    if key==27: # Press ESC to exit
        break
    elif key==ord('q'):
        cv2.imwrite('imgs/img.png', test_window)

cap.release()
cv2.destroyAllWindows()
