#include <BasicLinearAlgebra.h>
#include <iostream>

#ifndef MotionModel_h
#define MotionModel_h
// Global variables, will eventually will need to be changed to better match the model  (so essentially will have to be scaled.)  This is especially true if localization is desired.
extern float scaleFactor = .65; //Based on the results of the analysis, this may need to be increased by 5-10% to help the model be closer to a mean where the true location is.

class MotionModel
{
private:
  //functions
  BLA::Matrix<3, 12> rotX(BLA::Matrix<3, 12> inputVector, float degrees);
  BLA::Matrix<3, 12> rotY(BLA::Matrix<3, 12> inputVector, float degrees);
  BLA::Matrix<3, 12> rotZ(BLA::Matrix<3, 12> inputVector, float degrees);

  BLA::Matrix<3> rotYAccel(BLA::Matrix<3> inputVector, float degrees);
  BLA::Matrix<3> rotZAccel(BLA::Matrix<3> inputVector, float degrees);

  BLA::Matrix<2> sameSetElements(BLA::Matrix<3> matrix1, BLA::Matrix<3> matrix2);
  BLA::Matrix<2> uniqueSetElements(BLA::Matrix<3> matrix1, BLA::Matrix<3> matrix2);

  BLA::Matrix<3> nextCurrentBaseFunc(int similarBaseNode, BLA::Matrix<3> previousBase, BLA::Matrix<3> currentBase);

  BLA::Matrix<3> getCOM(BLA::Matrix<3> firstNode, BLA::Matrix<3> secondNode, BLA::Matrix<3> thirdNode);

  //FOR DETERMINING THE ROTATION AND POSITION OF THE ROBOT AFTER IT HAS ROLLED.
  BLA::Matrix<3, 3> determineRotMat(BLA::Matrix<3> node1Init, BLA::Matrix<3> node1Final, BLA::Matrix<3> node2Init, BLA::Matrix<3> node2Final, BLA::Matrix<3> node3Init, BLA::Matrix<3> node3Final);


  // variables
  BLA::Matrix<3, 12> initialNodes;
  BLA::Matrix<3> previousBaseNodes;
  BLA::Matrix<3, 12> previousSystemState;
  const BLA::Matrix<6, 6> R_uncert = { .2, 0, 0, 0, 0, 0,
                                      0, .2, 0, 0, 0, 0,
                                      0, 0, .1, 0, 0, 0,
                                      0, 0, 0, .1, 0, 0,
                                      0, 0, 0, 0, .1, 0,
                                      0, 0, 0, 0, 0, .1 };  //5cm for x and y because it seems larger than we expect. 0.1 for quaternion is a 5% error range
  float STRING_LENGTH; // To be used for position extrapolations

  BLA::Matrix<3, 12> initialNodes_T;

  const BLA::Matrix<30, 2> stringConnsSimple = { 1, 3, 1, 5, 1, 6, 1, 9, 1, 10, 2, 4, 2, 5, 2, 6, 2, 11, 2, 12, 3, 7, 3, 8, 3, 9,
                                                3, 10, 4, 7, 4, 8, 4, 11, 4, 12, 5, 6, 5, 9, 5, 11, 6, 10, 6, 12, 7, 8, 7, 9, 7,
                                                11, 8, 10, 8, 12, 9, 11, 10, 12 };

public:
  MotionModel();

// To be used for position extrapolations
float const STRING_LENGTH = (initialNodes(0, 0) - initialNodes(0, 2));
  //const variables
  const float scaleFactor = .65;

  //variables
  BLA::Matrix<3, 12> initialNodes_T2;

  //functions
  BLA::Matrix<3> getBase(BLA::Matrix<3> accel1); //FOR DETERMINING THE BASE OF THE SYSTEM IN ITS CURRENT CONFIGURATION.
  void propogateSystem(BLA::Matrix<3> accel, BLA::Matrix<3> estimatedState, BLA::Matrix<3, 3> R_total, BLA::Matrix<6,6> Sigma, BLA::Matrix<3> &estimatedState_bar, BLA::Matrix<3, 3> &R_bar, BLA::Matrix<6,6> & Sigma_bar);
};
#endif
