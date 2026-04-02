import numpy as np

# actual (0,6)
Corner2Corner = np.array(
    [[-0.01, 6.00], [-0.80, 6.26], [-0.90, 5.63], [2.85, 5.47], [-0.80, 6.04], [-0.26, 5.28], [-0.79, 4.90], [-0.50, 5.18], [-0.66, 5.61], [-0.42, 5.26]])
# actual (3,6)
Left2Middle = np.array(
    [[1.79, 5.72], [1.78, 5.70], [2.62, 5.16], [1.77, 5.66], [2.61, 5.12], [2.46, 5.28], [2.63, 5.43], [1.77, 5.74], [1.95, 5.67], [2.97, 4.83]])
# actual (6,6)
Left2Right = np.array(
    [[4.42, 6.42], [5.11, 6.93], [4.47, 7.28], [4.44, 5.56], [4.47, 6.34], [4.69, 6.36], [4.49, 6.43], [4.58, 6.47], [4.61, 6.43], [4.59, 6.47]])

# actual (-3,6)
Right2MiddleCorrected = np.array(
    [[-2.90, 6.01], [-2.81, 6.55], [-2.80, 6.65], [-2.74, 6.57], [-2.23, 6.38], [-2.83, 6.62], [-2.82, 6.61], [-2.76, 6.67], [-2.78, 6.59], [-2.82, 6.63]])

# actual(-6,-6)
Right2LeftCorrected = np.array(
    [[-6.17, 4.08], [-5.67, 4.66], [-5.76, 5.73], [-5.77, 5.76], [-5.68, 5.76], [-5.65, 5.72], [-5.65, 5.72], [-5.64, 5.76], [-5.77, 5.75], [-5.80, 5.77]])

# actual (0,6)
Corner2CornerCorrected = np.array([[0.77, 6.03], [0.17, 5.70], [0.54, 5.90]])
# actual (3,6)
Left2MiddleCorrected = np.array([[3.69, 5.00], [3.27, 5.64], [2.43, 5.66]])
# actual (6,6)
Left2RightCorrected = np.array([[6.20, 5.57], [5.96, 5.76], [5.66, 5.56]])

# Actual Location (0,0)
Corner2CornerBack = np.array([[-0.42, -0.36], [-0.42, -0.36], [0.12, 0.20], [-1.25, 0.91], [-1.30, 0.51]])
Left2RightBack = np.array([[1.44, -0.40], [0.73, -0.18], [2.38, 0.21], [-0.63, 0.52], [1.50, -1.04]])


print("\nCorner2Corner: ")
print("Mean: ", np.mean(Corner2Corner, axis=0))
print("Standard Deviation: ", np.std(Corner2Corner, axis=0))
modified_corner = Corner2Corner
modified_corner[:, 1] = modified_corner[:, 1] - 6
modified_corner_dist = np.sqrt(modified_corner[:, 0] ** 2 + modified_corner[:, 1] ** 2)
print("Mean Distance From Target: ", modified_corner_dist.mean())
print("Standard Deviation of Distance From Target: ", modified_corner_dist.std())
print("Mean Distance as percentage of distance traveled: ", modified_corner_dist.mean()/6)

print("\nLeft2Middle: ")
print("Mean: ", np.mean(Left2Middle, axis=0))
print("Standard Deviation: ", np.std(Left2Middle, axis=0))
modified_left2mid = Left2Middle
modified_left2mid[:, 0] = modified_left2mid[:, 0] - 3
modified_left2mid[:, 1] = modified_left2mid[:, 1] - 6
modified_left2mid_dist = np.sqrt(modified_left2mid[:, 0] ** 2 + modified_left2mid[:, 1] ** 2)
print("Mean Distance From Target: ", modified_left2mid_dist.mean())
print("Standard Deviation of Distance From Target: ", modified_left2mid_dist.std())
print("Mean Distance as percentage of distance traveled: ", modified_left2mid_dist.mean()/np.sqrt(6**2 + 3**2))

print("\nLeft2Right: ")
print("Mean: ", np.mean(Left2Right, axis=0))
print("Standard Deviation: ", np.std(Left2Right, axis=0))
modified_left2right = Left2Right
modified_left2right[:, 0] = modified_left2right[:, 0] - 6
modified_left2right[:, 1] = modified_left2right[:, 1] - 6
modified_left2right_dist = np.sqrt(modified_left2right[:, 0] ** 2 + modified_left2right[:, 1] ** 2)
print("Mean Distance From Target: ", modified_left2right_dist.mean())
print("Standard Deviation of Distance From Target: ", modified_left2right_dist.std())
print("Mean Distance as percentage of distance traveled: ", modified_left2right_dist.mean()/np.sqrt(6**2 + 6**2))

print("\nRight2MiddleCorrected: ")
print("Mean: ", np.mean(Right2MiddleCorrected, axis=0))
print("Standard Deviation: ", np.std(Right2MiddleCorrected, axis=0))
modified_right2mid = Right2MiddleCorrected
modified_right2mid[:, 0] = modified_right2mid[:, 0] + 3
modified_right2mid[:, 1] = modified_right2mid[:, 1] - 6
modified_right2mid_dist = np.sqrt(modified_right2mid[:, 0] ** 2 + modified_right2mid[:, 1] ** 2)
print("Mean Distance From Target: ", modified_right2mid_dist.mean())
print("Standard Deviation of Distance From Target: ", modified_right2mid_dist.std())
print("Mean Distance as percentage of distance traveled: ", modified_right2mid_dist.mean()/np.sqrt(6**2 + 3**2))

print("\nRight2LeftCorrected: ")
print("Mean: ", np.mean(Right2LeftCorrected, axis=0))
print("Standard Deviation: ", np.std(Right2LeftCorrected, axis=0))
modified_right2left = Right2LeftCorrected
modified_right2left[:, 0] = modified_right2left[:, 0] + 6
modified_right2left[:, 1] = modified_right2left[:, 1] - 6
modified_right2left_dist = np.sqrt(modified_right2left[:, 0] ** 2 + modified_right2left[:, 1] ** 2)
print("Mean Distance From Target: ", modified_right2left_dist.mean())
print("Standard Deviation of Distance From Target: ", modified_right2left_dist.std())
print("Mean Distance as percentage of distance traveled: ", modified_right2left_dist.mean()/np.sqrt(6**2 + 6**2))

print("\nCorner2CornerCorrected: ")
print("Mean: ", np.mean(Corner2CornerCorrected, axis=0))
print("Standard Deviation: ", np.std(Corner2CornerCorrected, axis=0))
modified_corner = Corner2CornerCorrected
modified_corner[:, 1] = modified_corner[:, 1] - 6
modified_corner_dist = np.sqrt(modified_corner[:, 0] ** 2 + modified_corner[:, 1] ** 2)
print("Mean Distance From Target: ", modified_corner_dist.mean())
print("Standard Deviation of Distance From Target: ", modified_corner_dist.std())
print("Mean Distance as percentage of distance traveled: ", modified_corner_dist.mean()/6)

print("\nLeft2MiddleCorrected: ")
print("Mean: ", np.mean(Left2MiddleCorrected, axis=0))
print("Standard Deviation: ", np.std(Left2MiddleCorrected, axis=0))
modified_left2mid = Left2MiddleCorrected
modified_left2mid[:, 0] = modified_left2mid[:, 0] - 3
modified_left2mid[:, 1] = modified_left2mid[:, 1] - 6
modified_left2mid_dist = np.sqrt(modified_left2mid[:, 0] ** 2 + modified_left2mid[:, 1] ** 2)
print("Mean Distance From Target: ", modified_left2mid_dist.mean())
print("Standard Deviation of Distance From Target: ", modified_left2mid_dist.std())
print("Mean Distance as percentage of distance traveled: ", modified_left2mid_dist.mean()/np.sqrt(6**2 + 3**2))

print("\nLeft2RightCorrected: ")
print("Mean: ", np.mean(Left2RightCorrected, axis=0))
print("Standard Deviation: ", np.std(Left2RightCorrected, axis=0))
modified_left2right = Left2RightCorrected
modified_left2right[:, 0] = modified_left2right[:, 0] - 6
modified_left2right[:, 1] = modified_left2right[:, 1] - 6
modified_left2right_dist = np.sqrt(modified_left2right[:, 0] ** 2 + modified_left2right[:, 1] ** 2)
print("Mean Distance From Target: ", modified_left2right_dist.mean())
print("Standard Deviation of Distance From Target: ", modified_left2right_dist.std())
print("Mean Distance as percentage of distance traveled: ", modified_left2right_dist.mean()/np.sqrt(6**2 + 6**2))

print("\nCorner2CornerBack: ")
print("Mean: ", np.mean(Corner2CornerBack, axis=0))
print("Standard Deviation: ", np.std(Corner2CornerBack, axis=0))
modified_left2right = Corner2CornerBack
modified_left2right_dist = np.sqrt(modified_left2right[:, 0] ** 2 + modified_left2right[:, 1] ** 2)
print("Mean Distance From Target: ", modified_left2right_dist.mean())
print("Standard Deviation of Distance From Target: ", modified_left2right_dist.std())
print("Mean Distance as percentage of distance traveled: ", modified_corner_dist.mean()/12)

print("\nLeft2RightBack: ")
print("Mean: ", np.mean(Left2RightBack, axis=0))
print("Standard Deviation: ", np.std(Left2RightBack, axis=0))
modified_left2right = Left2RightBack
modified_left2right[:, 0] = modified_left2right[:, 0]
modified_left2right[:, 1] = modified_left2right[:, 1]
modified_left2right_dist = np.sqrt(modified_left2right[:, 0] ** 2 + modified_left2right[:, 1] ** 2)
print("Mean Distance From Target: ", modified_left2right_dist.mean())
print("Standard Deviation of Distance From Target: ", modified_left2right_dist.std())
print("Mean Distance as percentage of distance traveled: ", modified_left2right_dist.mean()/2/np.sqrt(6**2 + 6**2))
