#=================================#
# Hand Gestures & Finger Counting #
#           with OpenCV           #
#           -----------           #
#       Konstantinos Thanos       #
#       Mathematician, MSc        #
#              2020               #
#=================================#

# Import libraries
import cv2
import math
import numpy as np

# Set text font
font = cv2.FONT_HERSHEY_PLAIN

# Video Capture from external camera
cap = cv2.VideoCapture(1)

# Define the Region Of Interest (ROI) window 
# Only inside this window the results will be visible
top_left = (245,150)
bottom_right = (580,395)

while True:
    _, frame = cap.read()
    # Horizontal flip (check if needed)
    frame = cv2.flip(frame, 1)

    # "Paint" with black color this area on the screen frame
    frame[0:40, 0:200] = (0)

    # Some text on screen
    cv2.putText(frame, "Fingers : ", (10,30), font, 2, (255,255,255), 2) 
    
    # Draw a rectangle (yellow color) around the ROI
    cv2.rectangle(frame, (top_left[0]-5,top_left[1]-5), (bottom_right[0]+5, bottom_right[1]+5), (0,255,255), 3)

    test_window = frame[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
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
        max_contour = max(contours, key=cv2.contourArea)
        # Draw maximum contour (blue color)
        cv2.drawContours(test_window, max_contour, -1, (255,0,0), 3)
        # Find the convex hull "around" the max_contour
        # --Convex Hull--
        convhull = cv2.convexHull(max_contour, returnPoints = True) 
        # Draw convex hull (red color)
        cv2.drawContours(test_window, [convhull], -1, (0,0,255), 3, 2)

        min_y = frame.shape[0] # Set the minimum y-value to a variable
        final_point = (frame.shape[1], frame.shape[0])
        for i in range(len(convhull)):
            point = (convhull[i][0][0], convhull[i][0][1])
            if point[1] < min_y:
                min_y = point[1]
                final_point = point
        # Draw a circle (black color) to the point with the minimum y-value (height)
        cv2.circle(test_window, final_point, 5, (0,0,0), 2)

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
#        cv2.fillPoly(test_window, [max_contour], (255,255,255)) 

        hull = cv2.convexHull(contour_poly, returnPoints = False) # --Hull--
        if len(hull) > 3:
            # Defect points
            defects = cv2.convexityDefects(contour_poly, hull)
            if type(defects) != type(None):
                count = 0
                test = []
                for i in range(defects.shape[0]): # Len of arrays
                    start_index, end_index, far_pt_index, fix_dept = defects[i][0]
                    start_pts = tuple(contour_poly[start_index][0])
                    end_pts = tuple(contour_poly[end_index][0])
                    mid_pts = (int((start_pts[0]+end_pts[0])/2), int((start_pts[1]+end_pts[1])/2))
                    test.append(mid_pts)
                    # Draw circle (yellow color in the mid_pts defect points)
                    cv2.circle(test_window, mid_pts, 2, (0,255,255), 2) 
                    far_pts = tuple(contour_poly[far_pt_index][0])
                    #--Start Points-- (yellow color)
#                    cv2.circle(test_window, start_pts, 2, (0,255,255), 2)
                    #--End Points-- (black color)
#                    cv2.circle(test_window, end_pts, 2, (0,0,0), 2)
                    #--Far Points-- (white color)
#                    cv2.circle(test_window, far_pts, 2, (255,255,255), 2)
#                    cv2.line(test_window, start_pts, end_pts, (200,200,255), 2)
#                    cv2.line(test_window, start_pts, far_pts, (200,200,255), 2)
#                    cv2.line(test_window, end_pts, far_pts, (20,20,25), 2)
                    # Distance between the start and the end defect point
                    a = math.sqrt((end_pts[0] - start_pts[0]) ** 2 + (end_pts[1] - start_pts[1]) ** 2)
                    # Distance between the farthest point and the start point
                    b = math.sqrt((far_pts[0] - start_pts[0]) ** 2 + (far_pts[1] - start_pts[1]) ** 2)
                    # Distance between the farthest point and the end point
                    c = math.sqrt((end_pts[0] - far_pts[0]) ** 2 + (end_pts[1] - far_pts[1]) ** 2)     
                    angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))  # Find each angle
                    # If angle > 90 then the farthest point is "outside the area of fingers"
                    if angle <= math.pi / 2:  
                        count += 1
                        cv2.circle(test_window, far_pts, 3, [0,255,255], -1)
                        frame[0:30, 170:200] = (0)
                        for c in range(5):
                            if count == c:
                                cv2.putText(frame, str(count+1), (170,30), font, 2, (255,255,255), 2)
                    if len(test) <= 1 :
                        frame[0:30, 170:200] = (0)
                        cv2.putText(frame, "1", (170,30), font, 2, (255,255,255), 2)
                    
   
    cv2.imshow("Frame", frame)
    
    key = cv2.waitKey(25)
    if key==27:
        break

cap.release()
cv2.destroyAllWindows()
