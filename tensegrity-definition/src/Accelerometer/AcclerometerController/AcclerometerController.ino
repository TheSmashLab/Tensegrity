/**************************************************************************/
/*!
    @file     AccelerometerController.C
    @author   B.Layer (BYU)
    @license  BSD (see license.txt)

    This code uses 3 Adafruit accelerometers to estimate the state of a tensegrity structure after

    @section  HISTORY

    v1.0  - First release
*/
/**************************************************************************/

#include <BasicLinearAlgebra.h>
#include "I2Cdev.h"
#include <math.h>
#include "MotionModel.h"
#include "MPU6050_6Axis_MotionApps20.h"
#include <SD.h>

#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
#include "Wire.h"
#endif

#define sgn(x) ((x) < 0 ? -1 : ((x) > 0 ? 1 : 0))

const int chipSelect = BUILTIN_SDCARD;
File testFile;

using namespace BLA;

MPU6050 mpu;

// The methods below are for the measurement update from measurements.
BLA::Matrix<4> quat_from_angles(BLA::Matrix<3> deltaAngles);
BLA::Matrix<3, 3> quat_to_R(BLA::Matrix<4> q);
BLA::Matrix<4> R_to_quat(BLA::Matrix<3, 3> R);

//State estimates
BLA::Matrix<3> estimatedState = { 0, 0, 0 };      //Estimated state after EKF
BLA::Matrix<3> estimatedState_bar = { 0, 0, 0 };  //Estimated state from motion model
BLA::Matrix<3> estimatedState_t = { 0, 0, 0 };    //Estimated state from measurement model


// Initialize total R
BLA::Matrix<3, 3> R_total = { 1, 0, 0, 0, 1, 0, 0, 0, 1 };  //Rotation matrix estimate
BLA::Matrix<3, 3> R_bar = { 1, 0, 0, 0, 1, 0, 0, 0, 1 };    //Rotation after motion model
BLA::Matrix<3, 3> R_t = { 1, 0, 0, 0, 1, 0, 0, 0, 1 };      //Rotation from measurment model at each time t
BLA::Matrix<3, 3> R_transform = { 0, 1, 0, 0, 0, 1, 1, 0, 0 };

// Uncertianty matrixes
BLA::Matrix<6,6> Sigma = {.02, 0, 0, 0, 0, 0,
                          0, .02, 0, 0, 0, 0,
                          0, 0, .1, 0, 0, 0,
                          0, 0, 0, .1, 0, 0,
                          0, 0, 0, 0, .1, 0,
                          0, 0, 0, 0, 0, .1};
BLA::Matrix<6,6> R_uncert = {.02, 0, 0, 0, 0, 0,
                              0, .02, 0, 0, 0, 0,
                              0, 0, 100, 0, 0, 0,
                              0, 0, 0, 100, 0, 0,
                              0, 0, 0, 0, 100, 0,
                              0, 0, 0, 0, 0, 100}; //.1 ft for x and y, since that represents an uncertainty from the motion of roughly 1 inch per timestep.
BLA::Matrix<6,6> Q_t = {.5, 0, 0, 0, 0, 0,
                          0, .5, 0, 0, 0, 0,
                          0, 0, .01, 0, 0, 0,
                          0, 0, 0, .01, 0, 0,
                          0, 0, 0, 0, .01, 0,
                          0, 0, 0, 0, 0, .01}; //Units for xy are in feet for testing

BLA::Matrix<2> momentum = {.04, .005}; //This matrix will be rotated every iteration and then added to the uncertainty created in the motion model.

float mean_slip = .00;


BLA::Matrix<3> v_tm1 = { 0, 0, 0 };

unsigned long previous_time;
int counter = 0;

int16_t ax, ay, az, gx, gy, gz;

// BLA::Matrix<3> gravity = { 0, 9.81, 0 };
const float bit_to_gravity = 1 / 8192.;


uint16_t packetSize;     // expected DMP packet size (default is 42 bytes)
uint16_t fifoCount;      // count of all bytes currently in FIFO
uint8_t fifoBuffer[64];  // FIFO storage buffer

//temp globals for debugging, will move around once completed TODO
Quaternion q_test;
VectorInt16 aa;       // [x, y, z]            accel sensor measurements
VectorInt16 aaReal;   // [x, y, z]            gravity-free accel sensor measurements
VectorInt16 aaWorld;  // [x, y, z]            world-frame accel sensor measurements
VectorFloat gravity;  // [x, y, z]            gravity vector
float dt;

float ACCEL_ROT_DEG = 80;

MotionModel motionModel;

// --------------------------------------- SETUP ----------------------------------------------------------------------------------------------------------------
void setup() {

// join I2C bus (I2Cdev library doesn't do this automatically)
  #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    Wire.begin();
    Wire.setClock(400000);  // 400kHz I2C clock. Comment this line if having compilation difficulties
  #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
    Fastwire::setup(400, true);
  #endif

  // initialize serial communication
  // (115200 chosen because it is required for Teapot Demo output, but it's
  // really up to you depending on your project)
  Serial.begin(38400);
  while (!Serial)

  // NOTE: 8MHz or slower host processors, like the Teensy @ 3.3V or Arduino
  // Pro Mini running at 3.3V, cannot handle this baud rate reliably due to
  // the baud timing being too misaligned with processor ticks. You must use
  // 38400 or slower in these cases, or use some kind of external separate
  // crystal solution for the UART timer.

  if (!SD.begin(chipSelect)) {
    Serial.println("Card failed, or not present");
  }
  else{
    Serial.println("Chip detected");
  }
  if(SD.exists("datalog.txt")){
    SD.remove("datalog.txt");
    testFile = SD.open("datalog.txt", FILE_WRITE);
    testFile.println('0,0,.1,0,0,.1');
    testFile.close();
  }

>>>>>>> main
  // initialize device
  Serial.println(F("Initializing I2C devices..."));
  
  mpu.initialize();
  mpu.dmpInitialize();


  // verify connection
  Serial.println(F("Testing device connections..."));
  Serial.println(mpu.testConnection() ? F("MPU6050 connection successful") : F("MPU6050 connection failed"));

  // wait for ready
  Serial.println(F("\nSend any character to begin DMP programming: "));
  while (Serial.available() && Serial.read())
    ;  // empty buffer
  while (!Serial.available())
    ;  // wait for data
  while (Serial.available() && Serial.read())
    ;  // empty buffer again

  // load and configure the DMP
  Serial.println(F("Initializing DMP..."));

  // supply your own gyro offsets here, scaled for min sensitivity
  mpu.setXGyroOffset(68);
  mpu.setYGyroOffset(79);
  mpu.setZGyroOffset(47);
  mpu.setXAccelOffset(-1620);
  mpu.setYAccelOffset(-450);
  mpu.setZAccelOffset(1000);  // 1688 factory default for my test chip

  // make sure it worked (returns 0 if so)

  packetSize = mpu.dmpGetFIFOPacketSize();
  previous_time = micros();

  mpu.CalibrateAccel(100);
  mpu.CalibrateGyro(100);

  mpu.setDMPEnabled(true);

  // Calibration Time: generate offsets and calibrate our MPU6050
  int counter = 0;
  while (counter < 100) {

    if (mpu.dmpGetCurrentFIFOPacket(fifoBuffer)) {
      counter++;
    }
  }
  Serial << "\n\n\n";
  Serial << "Base Nodes: " << previousBaseNodes(0) + 1 << ", " << previousBaseNodes(1) + 1 << ", " << previousBaseNodes(2) + 1 << "\n";
  Serial << estimatedState << "\n";
  previous_time = micros();
}
// --------------------------------------- END SETUP ----------------------------------------------------------------------------------------------------------------

// --------------------------------------- LOOP ----------------------------------------------------------------------------------------------------------------
// NOTE: Ensure that the nodes are properly lined up before testing the system. Otherwise, the internal orienation will not match the physical orientation, causing the model to make incorrect predictions.
//   In practice, this means you must ensure the initial nodes are oriented such that they move in the correct direction.
void loop() {
  if (mpu.dmpGetCurrentFIFOPacket(fifoBuffer)) {
      counter++;
      mpu.dmpGetQuaternion(&q_test, fifoBuffer);
      BLA::Matrix<4> q_mat = {q_test.w, q_test.x, q_test.y, q_test.z};
      q_mat = q_mat/BLA::Norm(q_mat);

    R_t = quat_to_R(q_mat);

      mpu.dmpGetAccel(&aa, fifoBuffer);
      BLA::Matrix<3> accel_robot = {aa.x*bit_to_gravity, aa.y*bit_to_gravity, aa.z*bit_to_gravity};
      // mpu.dmpGetGravity(&gravity, &q_test);
      // mpu.dmpGetLinearAccel(&aaReal, &aa, &gravity);
      // mpu.dmpGetLinearAccelInWorld(&aaWorld, &aaReal, &q_test);

      // BLA::Matrix<3> accel_r = {aaWorld.x*bit_to_gravity, aaWorld.y*bit_to_gravity, aaWorld.z*bit_to_gravity};
      BLA::Matrix<3> accel_r = R_t * accel_robot;
      accel_r(2) -= 9.81;

      if(abs(accel_r(0)) < .1){
        accel_r(0) = 0;
      }
      if(abs(accel_r(1)) < .1){
        accel_r(1) = 0;
      }
      if(abs(accel_r(2)) < .2){
        accel_r(2) = 0;
      }

      // if (accel_r(0) != 0 || accel_r(1) != 0 || accel_r(2) != 0){
      //   Serial << accel_robot << "\n";
      //   Serial << quat_to_R(q_mat) << "\n";
      //   Serial << accel_r <<"\n\n\n";  //Weird stuff with this term for some rotations, seems like the accelerometer gets rotated to far or something along those lines. Need to ask Dr. Hill.
      // }

      unsigned long current_time = micros();
      dt = (current_time - previous_time) / 1000000.0;
      previous_time = micros();
      float num = 1.3;
      estimatedState_t = estimatedState_t + (accel_r * float(pow(dt, 2)/2.) + v_tm1 * dt)/num;
      v_tm1 += accel_r * dt;

      if (counter % 400 == 0) {
        mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
        BLA::Matrix<3> accel1 = { ax * bit_to_gravity, ay * bit_to_gravity, az * bit_to_gravity };
        
        // The order that the accelerometers are given as inputs seems off because it needs to be given in the order that the get base expects, meaning accel 3 is 1,0,0.
        BLA::Matrix<3> currentBaseNodes = getBase(accel1);
        
        if (are_same_bases(currentBaseNodes, previousBaseNodes)){
          v_tm1 = {0, 0, 0};
          estimatedState_t = estimatedState;
          R_t = R_total;
          Serial << "\nSystem did not move.\n";
        }
        else{
          testFile = SD.open("datalog.txt", FILE_WRITE);
          // After getBase is completed, the code will need to keep track of the previous base, as well as the current base.
          // The previous base and the current base will be updated each time step as a result of predicting the base, and then propogating the motion of that base.
          Serial << "\n\n\n";
          Serial << "Base Nodes: " << currentBaseNodes(0) + 1 << ", " << currentBaseNodes(1) + 1 << ", " << currentBaseNodes(2) + 1 << "\n";
          Serial << estimatedState << "\n";

          BLA::Matrix<3> tmp = estimatedState;

          propogateSystem(previousBaseNodes, currentBaseNodes, currentNodes, estimatedState, R_total, estimatedState_bar, R_bar);
          Serial << estimatedState_bar << "\n";
          BLA::Matrix<6,6> Sigma_bar = Sigma + R_uncert;
          BLA::Matrix<3> movement = (estimatedState_bar - estimatedState)/BLA::Norm(estimatedState_bar - estimatedState); //This is the vector in the direction of movement;
          BLA::Matrix<2> simple_movement = {movement(0),movement(1)};
          BLA::Matrix<2> perp_movement = {-1/movement(1),-1/movement(0)};

          float v_x = abs(simple_movement(0)*momentum(0)) + abs(perp_movement(0)*momentum(1));
          float v_y = abs(simple_movement(1)*momentum(0)) + abs(perp_movement(1)*momentum(1));

          Sigma_bar(0,0) = Sigma_bar(0,0) + v_x;
          Sigma_bar(1,1) = Sigma_bar(1,1) + v_y;

          BLA::Matrix<4> q_bar = R_to_quat(R_bar);

          // Setup for ekf
          BLA::Matrix<6> mu = {estimatedState_bar(0) + simple_movement(0)*mean_slip, estimatedState_bar(1)+ simple_movement(1)*mean_slip, q_bar(0), q_bar(1), q_bar(2), q_bar(3)};
          BLA::Matrix<6> mu_meas = {estimatedState_t(0), estimatedState_t(1), q_mat(0), q_mat(1), q_mat(2), q_mat(3)};

          //EKF
          BLA::Matrix<6,6> K = Sigma_bar * Inverse(Sigma_bar + Q_t);
          mu = mu + K * (mu_meas - mu);
          Sigma = Sigma_bar - K * Sigma_bar;

          Serial << "q bar: " << q_bar << "\n";
          Serial << "Estimated State: " << estimatedState_bar << "\n";

          Serial << "q_mat: " << q_mat << "\n";
          Serial << "Estimated State at t: " << estimatedState_t << "\n";

          Serial << "EKF: " << mu << "\n";
          for(int k =0; k < 2; k++){
            testFile.print(mu(k));
            testFile.print(',');
          }
          for(int k = 0; k < 2; k++){
            for(int l = 0; l < 2; l++){
            testFile.print(Sigma(k,l));
            testFile.print(',');
            }
          }
          testFile.println();

          //Prepare for next iteration
          R_total = quat_to_R(BLA::Matrix<4> {mu(2), mu(3), mu(4), mu(5)});

          estimatedState = BLA::Matrix<3> {mu(0), mu(1), 0}; //z is always zero
          estimatedState_t = estimatedState;

          R_t = R_total;
          q_test.w = mu(2);
          q_test.x = mu(3);
          q_test.y = mu(4);
          q_test.z = mu(5);
          // mpu.dmpOverrideQuaternion(q_test);
          v_tm1 = {0, 0, 0};
          testFile.close();
        }
      }
    }
  }
}

// --------------------------------------- END LOOP ----------------------------------------------------------------------------------------------------------------
bool are_same_bases(BLA::Matrix<3> firstBase, BLA::Matrix<3> secondBase){
  bool sameBase = true;
  for(int i = 0; i < 3; i++){
    bool differentNode = false;
    for(int j = 0; j < 3; j++){
      if(firstBase(i) == secondBase(j)){
        differentNode = true;
      }
    }
    if (!differentNode){
      sameBase = false;
    }
  }
  return sameBase;
}

BLA::Matrix<4> quat_from_angles(BLA::Matrix<3> deltaAngles) {
  BLA::Matrix<4> q = { cos(deltaAngles(0) / 2) * cos(deltaAngles(1) / 2) * cos(deltaAngles(2) / 2) + sin(deltaAngles(0) / 2) * sin(deltaAngles(1) / 2) * sin(deltaAngles(2) / 2),
                       sin(deltaAngles(0) / 2) * cos(deltaAngles(1) / 2) * cos(deltaAngles(2) / 2) - cos(deltaAngles(0) / 2) * sin(deltaAngles(1) / 2) * sin(deltaAngles(2) / 2),
                       cos(deltaAngles(0) / 2) * sin(deltaAngles(1) / 2) * cos(deltaAngles(2) / 2) + sin(deltaAngles(0) / 2) * cos(deltaAngles(1) / 2) * sin(deltaAngles(2) / 2),
                       cos(deltaAngles(0) / 2) * cos(deltaAngles(1) / 2) * sin(deltaAngles(2) / 2) - sin(deltaAngles(0) / 2) * sin(deltaAngles(1) / 2) * cos(deltaAngles(2) / 2) };

  return q;
}

BLA::Matrix<3, 3> quat_to_R(BLA::Matrix<4> q) {
  BLA::Matrix<3, 3> R = { pow(q(0), 2) + pow(q(1), 2) - pow(q(2), 2) - pow(q(3), 2), 2 * (q(1) * q(2) - q(0) * q(3)), 2 * (q(0) * q(2) + q(1) * q(3)),
                          2 * (q(1) * q(2) + q(0) * q(3)), pow(q(0), 2) - pow(q(1), 2) + pow(q(2), 2) - pow(q(3), 2), 2 * (q(2) * q(3) - q(0) * q(1)),
                          2 * (q(1) * q(3) - q(0) * q(2)), 2 * (q(0) * q(1) + q(2) * q(3)), pow(q(0), 2) - pow(q(1), 2) - pow(q(2), 2) + pow(q(3), 2) };

  return R;
}

BLA::Matrix<4> R_to_quat(BLA::Matrix<3, 3> R) {
  BLA::Matrix<4> q = { .5 * sqrt(R(0, 0) + R(1, 1) + R(2, 2) + 1),
                       .5 * (sgn(R(2, 1) - R(1, 2)) * sqrt(R(0, 0) - R(1, 1) - R(2, 2) + 1)),
                       .5 * (sgn(R(0, 2) - R(2, 0)) * sqrt(R(1, 1) - R(2, 2) - R(0, 0) + 1)),
                       .5 * (sgn(R(1, 0) - R(0, 1)) * sqrt(R(2, 2) - R(0, 0) - R(1, 1) + 1)) };
  return q;
}

/********************************************************************************************
THE CODE BELOW IS FOR FILTERING THE ACCELEROMETER DATA TO BETTER DETERMINE SYSTEM STATE.
*********************************************************************************************/
