import math
import cv2
from time import time
import mediapipe as mp
import matplotlib.pyplot as plt
import winsound

# Initialize mediapipe pose model
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.3, model_complexity=2)

def detect_pose(image, pose, time1, display=True):
    # Create a copy of the input image.
    output_image = image.copy()

    # Convert the image from BGR into RGB format.
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Perform the Pose Detection.
    results = pose.process(image_rgb)

    # Retrieve the height and width of the input image.
    height, width, _ = image.shape

    # Initialize a list to store the detected landmarks.
    landmarks = []

    # Check if any landmarks are detected.
    if results.pose_landmarks:
        # Draw Pose landmarks on the output image.
        mp_drawing.draw_landmarks(image=output_image, landmark_list=results.pose_landmarks,
                                  connections=mp_pose.POSE_CONNECTIONS)

        # Iterate over the detected landmarks.
        for landmark in results.pose_landmarks.landmark:
            # Append the landmark into the list.
            landmarks.append((int(landmark.x * width), int(landmark.y * height), int(landmark.z * width)))

        # Classify the pose based on the detected landmarks and angles.
        output_image, label = classifyPose(landmarks, output_image, display=False)

        # Write FPS and classified label on the image.
        time2 = time()
        fps = 1.0 / (time2 - time1)
        fps_text = f'FPS: {fps:.2f}'
        cv2.putText(output_image, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(output_image, f'Pose: {label}', (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Check if the original input image and the resultant image are specified to be displayed.
    if display:
        # Display the output image.
        cv2.imshow('Pose Detection', output_image)

    # Return the output image and the found landmarks.
    return output_image, landmarks

def classifyPose(landmarks, output_image, display=False):
    '''
    This function classifies yoga poses depending upon the angles of various body joints.
    Args:
        landmarks: A list of detected landmarks of the person whose pose needs to be classified.
        output_image: A image of the person with the detected pose landmarks drawn.
        display: A boolean value that is if set to true the function displays the resultant image with the pose label 
        written on it and returns nothing.
    Returns:
        output_image: The image with the detected pose landmarks drawn and pose label written.
        label: The classified pose label of the person in the output_image.

    '''
    
    # Initialize the label of the pose. It is not known at this stage.
    label = 'Unknown Pose'

    # Specify the color (Red) with which the label will be written on the image.
    color = (0, 0, 255)
    
    # Calculate the required angles.
    #----------------------------------------------------------------------------------------------------------------
    
    # Get the angle between the left shoulder, elbow and wrist points. 
    left_elbow_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
                                      landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
                                      landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value])
    
    # Get the angle between the right shoulder, elbow and wrist points. 
    right_elbow_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
                                       landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value],
                                       landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value])   
    
    # Get the angle between the left elbow, shoulder and hip points. 
    left_shoulder_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
                                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
                                         landmarks[mp_pose.PoseLandmark.LEFT_HIP.value])

    # Get the angle between the right hip, shoulder and elbow points. 
    right_shoulder_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
                                          landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
                                          landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value])

    # Get the angle between the left hip, knee and ankle points. 
    left_knee_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
                                     landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value],
                                     landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value])

    # Get the angle between the right hip, knee and ankle points 
    right_knee_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
                                      landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value],
                                      landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value])
    
    # Get the angle between the left shoulder, hip, and knee points.
    left_hip_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
                                    landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
                                    landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value])
    
    # Get the angle between the right shoulder, hip, and knee points.
    right_hip_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
                                     landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
                                     landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value])

    
    #----------------------------------------------------------------------------------------------------------------
    
    # Check if it is the warrior II pose or the T pose.
    # As for both of them, both arms should be straight and shoulders should be at the specific angle.
    #----------------------------------------------------------------------------------------------------------------
    
    # Check if the both arms are straight.
    if left_elbow_angle > 165 and left_elbow_angle < 195 and right_elbow_angle > 165 and right_elbow_angle < 195:

        # Check if shoulders are at the required angle.
        if left_shoulder_angle > 80 and left_shoulder_angle < 110 and right_shoulder_angle > 80 and right_shoulder_angle < 110:

    # Check if it is the warrior II pose.
    #----------------------------------------------------------------------------------------------------------------

            # Check if one leg is straight.
            if left_knee_angle > 165 and left_knee_angle < 195 or right_knee_angle > 165 and right_knee_angle < 195:

                # Check if the other leg is bended at the required angle.
                if left_knee_angle > 90 and left_knee_angle < 120 or right_knee_angle > 90 and right_knee_angle < 120:

                    # Specify the label of the pose that is Warrior II pose.
                    label = 'Warrior II Pose' 
                        
    #----------------------------------------------------------------------------------------------------------------
    
    # Check if it is the T pose.
    #----------------------------------------------------------------------------------------------------------------
    
            # Check if both legs are straight
            if left_knee_angle > 160 and left_knee_angle < 195 and right_knee_angle > 160 and right_knee_angle < 195:

                # Specify the label of the pose that is tree pose.
                label = 'T Pose'

    #----------------------------------------------------------------------------------------------------------------
    
    # Check if it is the tree pose.
    #----------------------------------------------------------------------------------------------------------------
    
    # Check if one leg is straight
    if left_knee_angle > 165 and left_knee_angle < 195 or right_knee_angle > 165 and right_knee_angle < 195:

        # Check if the other leg is bended at the required angle.
        if left_knee_angle > 315 and left_knee_angle < 335 or right_knee_angle > 25 and right_knee_angle < 45:

            # Specify the label of the pose that is tree pose.
            label = 'Tree Pose'
                
    #----------------------------------------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------------------------------#
        # Check if it is the Butterfly Pose.
    # Knees spread apart, feet together, upright torso.
    # Check if it is the Butterfly Pose.
    if (left_knee_angle > 60 and left_knee_angle < 120) and (right_knee_angle > 60 and right_knee_angle < 120) and \
       (left_hip_angle > 20 and left_hip_angle < 70) and (right_hip_angle > 20 and right_hip_angle < 70):

        # Optionally check the shoulders but make it less strict.
        if (left_shoulder_angle > 150 and right_shoulder_angle > 150):
            label = 'Butterfly Pose'
        else:
            label = 'Butterfly Pose'  # Still classify if the shoulders are not in the exact position
    
     # Check if one leg is straight (supporting the body)
    if (left_knee_angle > 165 and left_knee_angle < 195) or (right_knee_angle > 165 and right_knee_angle < 195):

        # Check if the other leg is bent and lifted (calf raised).
        if (left_knee_angle > 60 and left_knee_angle < 100) or (right_knee_angle > 60 and right_knee_angle < 100):

            # Specify the label of the pose that is One-Legged Stand.
            label = 'One-Legged Stand'
    
    #--------------------------------------------#
    # The side plank is characterized by one straight arm supporting the body, and straight alignment from shoulder to ankle.
    if (left_elbow_angle > 160 and left_elbow_angle < 180) and (left_hip_angle > 160 and left_hip_angle < 180):
        # Left side plank (left arm supports the body)
        label = 'Side Plank (Left)'

    elif (right_elbow_angle > 160 and right_elbow_angle < 180) and (right_hip_angle > 160 and right_hip_angle < 180):
        # Right side plank (right arm supports the body)
        label = 'Side Plank (Right)'


    # Check if the pose is classified successfully
    if label != 'Unknown Pose':
        
        # Update the color (to green) with which the label will be written on the image.
        color = (0, 255, 0)  
    else:
        winsound.Beep(1000,500)
    # Write the label on the output image. 
    cv2.putText(output_image, label, (10, 60),cv2.FONT_HERSHEY_PLAIN, 2, color, 2)
    
    # Check if the resultant image is specified to be displayed.
    if display:
    
        # Display the resultant image.
        plt.figure(figsize=[10,10])
        plt.imshow(output_image[:,:,::-1])
        plt.title("Output Image");plt.axis('off')
        
    else:
        
        # Return the output image and the classified label.
        return output_image, label


def calculateAngle(landmark1, landmark2, landmark3):
    '''
    This function calculates the angle between three different landmarks.
    Args:
        landmark1: The first landmark containing the x, y, and z coordinates.
        landmark2: The second landmark containing the x, y, and z coordinates.
        landmark3: The third landmark containing the x, y, and z coordinates.
    Returns:
        angle: The calculated angle between the three landmarks.
    '''
    x1, y1, _ = landmark1
    x2, y2, _ = landmark2
    x3, y3, _ = landmark3
    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
    if angle < 0:
        angle += 360
    return angle

def main():
    # Initialize the VideoCapture object to read from the webcam or video file.
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # Check if the camera or video file is opened successfully.
    if not cap.isOpened():
        print("Error: Unable to open camera or video file.")
        return

    # Initialize time1 for FPS calculation.
    time1 = time()

    # Create an OpenCV window with full-screen mode initially.
    cv2.namedWindow('Pose Detection', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('Pose Detection', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Loop until the user presses 'q' or the window is closed.
    while True:
        # Read a frame from the camera or video file.
        ret, frame = cap.read()

        # Check if frame is read successfully.
        if not ret:
            print("Error: Failed to capture frame from camera or video.")
            break

        # Detect pose in the frame.
        output_frame, _ = detect_pose(frame, pose, time1, display=False)

        # Display the frame with pose estimation.
        cv2.imshow('Pose Detection', output_frame)

        # Update time1 for FPS calculation.
        time1 = time()

        # Check for key press events
        key = cv2.waitKey(1)
        if key == ord('q'):  # Quit when 'q' is pressed
            break
        elif key == ord('f'):  # Toggle full-screen mode when 'f' is pressed
            fullscreen = not fullscreen
            if fullscreen:
                cv2.setWindowProperty('Pose Detection', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            else:
                cv2.setWindowProperty('Pose Detection', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

    # Release the VideoCapture object and close all windows.
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
