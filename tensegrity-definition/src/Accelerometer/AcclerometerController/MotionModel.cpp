#include "MotionModel.h"

MotionModel::MotionModel() {
  initialNodes = BLA::Matrix<3,12>{ 1, 1, -1, -1, 1.618, 1.618, -1.618, -1.618, 0, 0, 0, 0,    //X Coords of the tensegrity system
                                  1.618, -1.618, 1.618, -1.618, 0, 0, 0, 0, 1, 1, -1, -1,    //Y Coords of the tensegrity system.
                                  0, 0, 0, 0, 1, -1, 1, -1, 1.618, -1.618, 1.618, -1.618 } 
                                  * scaleFactor;

  STRING_LENGTH = (initialNodes(0, 0) - initialNodes(0, 2));

  initialNodes_T = rotZ(initialNodes, 135);
  initialNodes_T2 = rotZ(~(~rotY(initialNodes_T, 35) * ~BLA::Matrix<3,3> {0,1,0,0,0,1,1,0,0}), -140);

  previousBaseNodes = { 0, 5, 9 };  //Corresponds to nodes 1, 6, 10

  previousSystemState = initialNodes_T2;
}

/**
 * Calculates the X rotation of an system state to create the initial state that matches assumptions of what the first node down is.
 *
 * @param inputVector A 3x12 vector representing the state of the system.
 * @param degrees The number of degrees to rotate the system.
 * @return The rotated input state.
 */
BLA::Matrix<3, 12> MotionModel::rotX(BLA::Matrix<3, 12> inputVector, float degrees) {
  float radDegs = degrees / 180. * 3.141592;
  BLA::Matrix<3, 3> rotXMat{ 1, 0, 0,
                             0, cos(radDegs), -sin(radDegs),
                             0, sin(radDegs), cos(radDegs) };

  return rotXMat * inputVector;
}

/**
 * Calculates the Y rotation of an system state to create the initial state that matches assumptions of what the first node down is.
 *
 * @param inputVector A 3x12 vector representing the state of the system.
 * @param degrees The number of degrees to rotate the system.
 * @return The rotated input state.
 */
BLA::Matrix<3, 12> MotionModel::rotY(BLA::Matrix<3, 12> inputVector, float degrees) {
  float radDegs = degrees / 180. * 3.141592;
  BLA::Matrix<3, 3> rotYMat{ cos(radDegs), 0, sin(radDegs),
                             0, 1, 0,
                             -sin(radDegs), 0, cos(radDegs) };

  return rotYMat * inputVector;
}

/**
 * Calculates the Z rotation of an system state to create the initial state that matches assumptions of what the first node down is.
 *
 * @param inputVector A 3x12 vector representing the state of the system.
 * @param degrees The number of degrees to rotate the system.
 * @return The rotated input state.
 */
BLA::Matrix<3, 12> MotionModel::rotZ(BLA::Matrix<3, 12> inputVector, float degrees) {
  float radDegs = degrees / 180. * 3.141592;
  BLA::Matrix<3, 3> rotZMat{ cos(radDegs), -sin(radDegs), 0,
                             sin(radDegs), cos(radDegs), 0,
                             0, 0, 1 };

  return rotZMat * inputVector;
}

/**
 * Calculates the Y rotation of an accelerometer measurement to align the accelerometer measurement with the initial rotation undergone by the system.
 *
 * @param inputVector A 3x1 vector representing the vector to be rotated about the Y axis.
 * @param degrees The number of degrees to rotate the system.
 * @return The rotated input vector.
 */
BLA::Matrix<3> MotionModel::rotYAccel(BLA::Matrix<3> inputVector, float degrees) {
  float radDegs = degrees / 180. * 3.141592;
  BLA::Matrix<3, 3> rotYMat{ cos(radDegs), 0, sin(radDegs),
                             0, 1, 0,
                             -sin(radDegs), 0, cos(radDegs) };

  return rotYMat * inputVector;
}

/**
 * Rotates a 3D input vector around the Z-axis by the specified angle in degrees.
 *
 * @param inputVector The 3D vector to be rotated.
 * @param degrees The angle of rotation in degrees.
 * @return The rotated 3D vector.
 */
BLA::Matrix<3> MotionModel::rotZAccel(BLA::Matrix<3> inputVector, float degrees) {
  float radDegs = degrees / 180. * 3.141592;
  BLA::Matrix<3, 3> rotZMat{ cos(radDegs), -sin(radDegs), 0,
                             sin(radDegs), cos(radDegs), 0,
                             0, 0,  1};

  return rotZMat * inputVector;
}

/**
 * Determines the common values in 2 sets of numbers, with the unique elements of the first vector returned first.
 *
 * @param matrix1 A 3x1 vector containing 3 values
 * @param matrix2 A 3x1 vector containing 3 values, with 2 of the 3 values assumed to be the same as matrix 1.
 * @return The elements of the 2 vectors that are different, with the value of the first matrix returned first.
 */
BLA::Matrix<2> MotionModel::sameSetElements(BLA::Matrix<3> matrix1, BLA::Matrix<3> matrix2) {
  BLA::Matrix<2> sameElements{ -1, -1 };
  bool success = false;
  int counter = 0;

  for (int i = 0; i < 3; i++) {
    success = false;

    for (int j = 0; j < 3; j++) {
      if (matrix1(i) == matrix2(j)) {
        success = true;
      }
    }
    if (success) {
      sameElements(counter) = matrix1(i);
      counter += 1;
    }
  }

  return sameElements;
}

/**
 * Determines the unique values in 2 sets of numbers, with the unique elements of the first vector returned first.
 *
 * @param matrix1 A 3x1 vector containing 3 values
 * @param matrix2 A 3x1 vector containing 3 values, with 2 of the 3 values assumed to be the same as matrix 1.
 * @return The elements of the 2 vectors that are different, with the value of the first matrix returned first.
 */
BLA::Matrix<2> MotionModel::uniqueSetElements(BLA::Matrix<3> matrix1, BLA::Matrix<3> matrix2) {

  BLA::Matrix<2> uniqueElements{ -1, -1 };
  bool success = true;

  for (int i = 0; i < 3; i++) {
    success = true;

    for (int j = 0; j < 3; j++) {
      if (matrix1(i) == matrix2(j)) {
        success = false;
      }
    }
    if (success) {
      uniqueElements(0) = matrix1(i);
      break;
    }
  }

  for (int i = 0; i < 3; i++) {
    success = true;

    for (int j = 0; j < 3; j++) {
      if (matrix2(i) == matrix1(j)) {
        success = false;
      }
    }
    if (success) {
      uniqueElements(1) = matrix2(i);
      break;
    }
  }

  return uniqueElements;
}

/*
TODO: Add documentation
*/
BLA::Matrix<3> MotionModel::nextCurrentBaseFunc(int similarBaseNode, BLA::Matrix<3> previousBase, BLA::Matrix<3> currentBase) {
  int node1Conns[5];
  int node2Conns[5];
  int node1ConnCounter = 0;
  int node2ConnCounter = 0;

  for (int i = 0; i < stringConnsSimple.Rows; i++) {
    if (stringConnsSimple(i, 0) == similarBaseNode + 1) {
      node1Conns[node1ConnCounter] = stringConnsSimple(i, 1) - 1;
      node1ConnCounter += 1;
    }
    if (stringConnsSimple(i, 1) == similarBaseNode + 1) {
      node1Conns[node1ConnCounter] = stringConnsSimple(i, 0) - 1;
      node1ConnCounter += 1;
    }
  }

  int possibleTargetNode[2];
  int index = 0;

  for (int i = 0; i < 5; i++) {
    for (int j = 0; j < 3; j++) {
      if (node1Conns[i] == currentBase(j)) {
        possibleTargetNode[index] = node1Conns[i];
        index += 1;
      }
    }
  }

  int targetNode;
  for (int k = 0; k < 2; k++) {
    for (int i = 0; i < stringConnsSimple.Rows; i++) {
      if (stringConnsSimple(i, 0) == possibleTargetNode[k] + 1) {
        node2Conns[node2ConnCounter] = stringConnsSimple(i, 1) - 1;
        node2ConnCounter += 1;
      }
      if (stringConnsSimple(i, 1) == possibleTargetNode[k] + 1) {
        node2Conns[node2ConnCounter] = stringConnsSimple(i, 0) - 1;
        node2ConnCounter += 1;
      }
    }
    boolean correctNode = false;
    for (int i = 0; i < 5; i++) {
      for (int j = 0; j < 3; j++) {
        if (node2Conns[i] == previousBase(j) && node2Conns[i] != similarBaseNode) {
          correctNode = true;
        }
      }
    }
    if (correctNode) {
      targetNode = possibleTargetNode[k];
      break;
    }
    node2ConnCounter = 0;
  }

  int lastBaseNode;

  for (int i = 0; i < 5; i++) {
    for (int j = 0; j < 5; j++) {
      if (node1Conns[i] == node2Conns[j] && (node1Conns[i] == previousBase(0) || node1Conns[i] == previousBase(1) || node1Conns[i] == previousBase(2))) {
        lastBaseNode = node1Conns[i];
      }
    }
  }

  BLA::Matrix<3> nextCurrentBase = { similarBaseNode, targetNode, lastBaseNode };
  return nextCurrentBase;
}

/**
 * Calculates the base of the system by determining what base the accelerometer reading is "pointing" at.
 *
 * @param accel1 The accelerometer reading.
 * @return The 3 nodes that comprise the base of the system.
 */
BLA::Matrix<3> MotionModel::getBase(BLA::Matrix<3> accel1) {

  BLA::Matrix<12, 1> accelNodes = ~initialNodes_T2 * accel1;
  BLA::Matrix<3> minInd = { -1, -1, -1 };
  BLA::Matrix<3> minVals = { 1.0 / 0.0, 1.0 / 0.0, 1.0 / 0.0 };

  for (int i = 0; i < 12; i++) {
    // Serial.println(accelNodes(i));
    if (minVals(0) > accelNodes(i)) {

      minVals(2) = minVals(1);
      minInd(2) = minInd(1);
      minVals(1) = minVals(0);
      minInd(1) = minInd(0);
      minVals(0) = accelNodes(i);
      minInd(0) = i;
    } else if (minVals(1) > accelNodes(i)) {
      minVals(2) = minVals(1);
      minInd(2) = minInd(1);
      minVals(1) = accelNodes(i);
      minInd(1) = i;
    } else if (minVals(2) > accelNodes(i)) {
      minVals(2) = accelNodes(i);
      minInd(2) = i;
    }
  }
  //  Serial << minVals << "\n";
  return minInd;
}

/**
 * Determines the Center of mass of an array
 *
 * @param base A 3x1 vector representing the base of the system at its current location
 * @return A 3x1 vector representing the location of the system's current center of mass.
 */
BLA::Matrix<3> MotionModel::getCOM(BLA::Matrix<3> firstNode, BLA::Matrix<3> secondNode, BLA::Matrix<3> thirdNode) {  //TODO
  float x = firstNode(0);
  float y = firstNode(1);
  float z = firstNode(2);

  x = x + secondNode(0);
  y = y + secondNode(1);
  z = z + secondNode(2);

  x = x + thirdNode(0);
  y = y + thirdNode(1);
  z = z + thirdNode(2);

  x = x / 3;
  y = y / 3;
  z = z / 3;

  BLA::Matrix<3> COM = { x, y, z };
  return COM;
}

/**
 * Creates a rotation matrix that represents the rotation of the system between 2 bases given a 3 previous node and 3 current nodes. In order to achieve this matrix at each time step,
 * The entire system will have to be rotated each time step and stored so that the location of the base node previous to rotation can be calculated.
 *
 * @param node1Init A 3x1 vector representing one of the base nodes before rotation.
 * @param node1Final A 3x1 vector representing one of the base nodes after rotation.
 * @param node2Init A 3x1 vector representing one of the base nodes before rotation.
 * @param node2Final A 3x1 vector representing one of the base nodes after rotation.
 * @param node3Init A 3x1 vector representing one of the base nodes before rotation.
 * @param node3Final A 3x1 vector representing one of the base nodes after rotation.
 * @return The rotation matrix that describes the rotation that each node undergoes to reach the back nodes.
 */
BLA::Matrix<3, 3> MotionModel::determineRotMat(BLA::Matrix<3> node1Init, BLA::Matrix<3> node1Final, BLA::Matrix<3> node2Init, BLA::Matrix<3> node2Final, BLA::Matrix<3> node3Init, BLA::Matrix<3> node3Final) {

  // Normalizing these vectors helps if the estimate isn't quite correct to get a rotation matrix with a determinant closer to 1.
  node1Init = node1Init / BLA::Norm(node1Init);
  node1Final = node1Final / BLA::Norm(node1Final);
  node2Init = node2Init / BLA::Norm(node2Init);
  node2Final = node2Final / BLA::Norm(node2Final);
  node3Init = node3Init / BLA::Norm(node3Init);
  node3Final = node3Final / BLA::Norm(node3Final);

  BLA::Matrix<3, 3> F = { node1Final(0), node1Final(1), node1Final(2), node2Final(0), node2Final(1), node2Final(2), node3Final(0), node3Final(1), node3Final(2) };
  F = ~F;

  BLA::Matrix<3, 3> I = { node1Init(0), node1Init(1), node1Init(2), node2Init(0), node2Init(1), node2Init(2), node3Init(0), node3Init(1), node3Init(2) };
  I = ~I;
  Invert(I);

  BLA::Matrix<3, 3> R = F * I;  //I was inverted by reference

  // This is a good approximation of R. determinant is close to 1, we normalize the rows of R here since the movement is an approximation and we don't want significant expansion/ contraction of it.
  BLA::Matrix<3> R1 = { R(0, 0), R(0, 1), R(0, 2) };
  BLA::Matrix<3> R2 = { R(1, 0), R(1, 1), R(1, 2) };
  BLA::Matrix<3> R3 = { R(2, 0), R(2, 1), R(2, 2) };

  R = { R1(0), R1(1), R1(2), R2(0), R2(1), R2(2), R3(0), R3(1), R3(2) };

  return R;
}

/**
 * Determines the unique values in 2 sets of numbers, with the unique elements of the first vector returned first.
 * TODO: fill out documentation
 */
void MotionModel::propogateSystem(BLA::Matrix<3> accel, BLA::Matrix<3> estimatedState, BLA::Matrix<3, 3> R_total, BLA::Matrix<6,6> Sigma, BLA::Matrix<3> &estimatedState_bar, BLA::Matrix<3, 3> &R_bar, BLA::Matrix<6,6> & Sigma_bar) {
  BLA::Matrix<3> currentBaseNodes = getBase(accel);

  //Step 0: Check if the system even rotated.
  bool basesEqual = true;

  for (int i = 0; i < 3; i++) {
    bool oneEqual = false;

    for (int j = 0; j < 3; j++) {

      if (previousBaseNodes(i) == currentBaseNodes(j)) {
        oneEqual = true;
      }
    }

    if (!oneEqual) basesEqual = false;
  }

  if (basesEqual){
    R_bar = R_total;
    estimatedState_bar = estimatedState;
    Sigma_bar = Sigma;
    return;
  }

  // Step 1: Determine the base path that the robot when through, and follow that.  We are assuming that the bases are no further than 2 steps apart.
  int counter = 0;
  int counterTotal;
  BLA::Matrix<2> elementSet = sameSetElements(previousBaseNodes, currentBaseNodes);

  if (elementSet(1) == -1) {
    counterTotal = 2;
  } else {
    counterTotal = 1;
  }

  BLA::Matrix<3> nextCurrentBase;

  // This is to determine the "next Current base".
  // TODO: This does not work robustly for any 2 rotations, needs to be fixed more.
  if (2 == counterTotal) {
    nextCurrentBase = nextCurrentBaseFunc(elementSet(0), previousBaseNodes, currentBaseNodes);
  } else {
    nextCurrentBase = currentBaseNodes;
  }

  // Currently works for 1 rotation perfectly, needs to be edited for 2 rotations.
  while (counter < counterTotal) {

    // Step 2: Find different nodes in the 2 bases.
    BLA::Matrix<2> differentNodes = uniqueSetElements(previousBaseNodes, nextCurrentBase);

    // Step 3: Find same nodes between the 2 vectors and find the pivot line between them.
    BLA::Matrix<2> sameNodes = sameSetElements(previousBaseNodes, nextCurrentBase);

    BLA::Matrix<3> firstNode = { previousSystemState(0, sameNodes(0)), previousSystemState(1, sameNodes(0)), previousSystemState(2, sameNodes(0)) };
    BLA::Matrix<3> secondNode = { previousSystemState(0, sameNodes(1)), previousSystemState(1, sameNodes(1)), previousSystemState(2, sameNodes(1)) };
    BLA::Matrix<2> pivotVector = { secondNode(0) - firstNode(0), secondNode(1) - firstNode(1) };

    // Step 4: Find the perpendicular unit vector to that vector on the Z plane.
    BLA::Matrix<2> perpendicularVector = { -1 * pivotVector(1), pivotVector(0) };
    BLA::Matrix<2> unitPerpendicularVector = perpendicularVector / BLA::Norm(perpendicularVector);

    // Step 5: Find the midpoint of the 2 pivot nodes
    BLA::Matrix<2> midPoint = { (secondNode(0) + firstNode(0)) / 2, (secondNode(1) + firstNode(1)) / 2 };

    // Step 6: Use the current location of the current node and the midpoint to determine if the perp vector is facing the correct way.
    BLA::Matrix<2> directionVector = { previousSystemState(0, differentNodes(1)) - midPoint(0), previousSystemState(1, differentNodes(1)) - midPoint(1) };

    BLA::Matrix<1> check = ~directionVector * unitPerpendicularVector;
    if (0 > check(0)) {
      unitPerpendicularVector = unitPerpendicularVector * float(-1);
    }

    // Step 7: Set the x,y coordinates of the new node to the mid-point of the 2 nodes, plus the perpendicular vector times the length of the string* sqrt(3)/2 (assuming equilateral)
    // Step 8: Set the z coordinate to the average of the z coordinates of the 2 constant nodes.

    // The 2/3 here is because the center of mass of the system travels the shorted centroid distance of a triangle 2x (meaning 1 centroid distance to the roation axis, and then one more from the axis to rest.)
    // The sqrt(3)/2 is here to get the actual distance that the triangle axis is. (meaning the height of a equilateral tria)
    BLA::Matrix<2> displacement = unitPerpendicularVector * float(STRING_LENGTH * sqrt(3) / 2);
//    Serial << previousSystemState << "\n";
    BLA::Matrix<3> currentLoc = { midPoint(0) + displacement(0),
                                  midPoint(1) + displacement(1),
                                   (previousSystemState(2, sameNodes(1)) + previousSystemState(2, sameNodes(0))) / 2 };

    // Step 9: Find the centroid of the current nodes and the new node now located on the ground.
    BLA::Matrix<3> COM = getCOM(firstNode, secondNode, currentLoc);

    //We don't want the nodes to be translated up to the center, want the system centered about 0, not the base.
    COM(2) = 0;

    // Step 10: Subtract out the centroid to move the model to be located about the origin again.
    BLA::Matrix<3> alteredFirstNode = firstNode - COM;
    BLA::Matrix<3> alteredSecondNode = secondNode - COM;
    BLA::Matrix<3> alteredThirdNode = currentLoc - COM;

    BLA::Matrix<3> originalNode = { previousSystemState(0, differentNodes(1)), previousSystemState(1, differentNodes(1)), previousSystemState(2, differentNodes(1)) };

    // Step 11:  Use the new points as well as the old points to find the rotation matrix that makes that transformation possible.
    BLA::Matrix<3, 3> R = determineRotMat(firstNode, alteredFirstNode, secondNode, alteredSecondNode, originalNode, alteredThirdNode);

    // Update system parameters. In this case, these are global variables declared at the beginning.
    previousBaseNodes = nextCurrentBase;
    nextCurrentBase = currentBaseNodes;

    R_bar = R_total * R;

    // This estimated state implementation might work, since all that the COM is used for is moving the location of the new base back to the origin. In this case,
    // We can also scale the COM estimate based on how the actual model scales to the simulated model.
    // TODO: VALIDATE THIS ESTIMATED STATE MODEL!
    estimatedState_bar = estimatedState + COM * scaleFactor;

    // So doing this is valid because it doesn't actually move the system, the current nodes are always centered about 0.  The actual state of the system would be the
    // rotated nodes plus the estimated displacement.
    previousSystemState = R * previousSystemState;
    Sigma_bar = Sigma + R_uncert;
    counter++;
  }
}
