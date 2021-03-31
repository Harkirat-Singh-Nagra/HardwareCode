import board
import busio
import RPi.GPIO as GPIO
import adafruit_bme280

from time import sleep
import pyrebase

from mq import *
import sys, time


# Create library object using our Bus I2C port
i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

GPIO.setmode(GPIO.BOARD)

GPIO.setup(36, GPIO.IN) #PIR
GPIO.setup(32, GPIO.OUT) #BUZZER

# OR create library object using our Bus SPI port
# spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
# bme_cs = digitalio.DigitalInOut(board.D10)
# bme280 = adafruit_bme280.Adafruit_BME280_SPI(spi, bme_cs)

# change this to match the location's pressure (hPa) at sea level
bme280.sea_level_pressure = 1013.25

# configuration of the database access
# Global objects: config and user
# ====================================================================================================
config = {
    "apiKey": "AIzaSyA_AW-u9CM1CepLI3Tl0t_hKr2yJtjRX20",
    "authDomain": "milestone-52414.firebaseapp.com",
    "databaseURL": "https://milestone-52414-default-rtdb.firebaseio.com/",
    "storageBucket": "milestone-52414.appspot.com",
}
user = None  # define user as a global variable to access from all the functions.
# ====================================================================================================

# The authorization function
# ====================================================================================================
def GetAuthorized(firebase):
    global user
    auth = firebase.auth()  # Get a reference to the auth service
    # authenticate a user
    try:
        user = auth.sign_in_with_email_and_password("chillmill@gmail.com",
                                                    "chillmill")  # username and password of your account for database
#       print(user)  # display the user information, if successful
    except:
        print("Not authorized")
        user = None

# The function to initialize the database.
# ====================================================================================================
def dbInitialization():
    firebase = pyrebase.initialize_app(config)  # has to initialize the database
    GetAuthorized(firebase)  # get authorized to operate on the database.
    return firebase

# The function to send the data to firebase database.
# ====================================================================================================
def sendtoMQ2Firebase(db, mq2data):
    result = db.child("mq2").push(mq2data, user["idToken"])  # needs the authorization to save the data
    print(result)
    return;

# The function to send the data to firebase database.
# ====================================================================================================
def sendtoBMEFirebase(db, bmedata):
    result = db.child("bme280").push(bmedata, user["idToken"])  # needs the authorization to save the data
    print(result)
    return;

# The function to send the data to firebase database.
# ====================================================================================================
def sendtoPIRFirebase(db, pirdata):
    result = db.child("pir").push(pirdata, user["idToken"])  # needs the authorization to save the data
    print(result)
    return;

# The function to get the data from firebase database.
# ====================================================================================================
def GetMQ2DatafromFirebase(db):
    results = db.child("mq2").get(user["idToken"]).val();  # needs the authorization to get the data.
    print("These are the records from the Database")
    print(results)
    return;

# The function to get the data from firebase database.
# ====================================================================================================
def GetBMEDatafromFirebase(db):
    results = db.child("bme280").get(user["idToken"]).val();  # needs the authorization to get the data.
    print("These are the records from the Database")
    print(results)
    return;

# The function to get the data from firebase database.
# ====================================================================================================
def GetPIRDatafromFirebase(db):
    results = db.child("pir").get(user["idToken"]).val();  # needs the authorization to get the data.
    print("These are the results from the Database")
    print(results)
    return;

# The function to set up the record structure to be written to the database.
# ====================================================================================================
def setupMQ2Data(co, lpg, smoke, timestamp):
    mq2sensor = {"co": co,
                 "lpg": lpg,
                 "smoke": smoke,
                 "timestamp": timestamp}  # always post the timestamps in epoch with the data to track the timing.
                                        # Store the data as the dictionary format in python  # refer to here:
                                        # https://www.w3schools.com/python/python_dictionaries.asp
    return mq2sensor

# The function to set up the record structure to be written to the database.
# ====================================================================================================
def setupBMEData(humidity, pressure, temp, timestamp):
    bmesensor = {"humidity": humidity,
                 "pressure": pressure,
                 "temp": temp,
                 "timestamp": timestamp}  # always post the timestamps in epoch with the data to track the timing.
                                        # Store the data as the dictionary format in python  # refer to here:
                                        # https://www.w3schools.com/python/python_dictionaries.asp
    return bmesensor

# The function to set up the record structure to be written to the database.
# ====================================================================================================
def setupPIRData(motion_detected, buzzer_state, timestamp):
    pirsensor = {"motion_detected": motion_detected,
              "buzzer_state": buzzer_state,
              "timestamp": timestamp}  # always post the timestamps in epoch with the data to track the timing.
                                        # Store the data as the dictionary format in python  # refer to here:
                                        # https://www.w3schools.com/python/python_dictionaries.asp
    return pirsensor

# The function to send the data to firebase database's user authorized section.
# Each user has a separate record tree, and it is only accessible for the authorized users.
# ====================================================================================================
def sendtoUserFirebase(db, mq2data,bmedata,pirdata):
    userid = user["localId"] # this will guarantee the data is stored into the user directory.
    result = db.child("userdata").child(userid).push(mq2data, user["idToken"])  # needs the authorization to save the data
    print(result)
    result = db.child("userdata").child(userid).push(bmedata, user["idToken"])  # needs the authorization to save the data
    print(result)
    result = db.child("userdata").child(userid).push(pirdata, user["idToken"])  # needs the authorization to save the data
    print(result)
    return;

# The following code would write and read the database with the authorized user
# ====================================================================================================
def testFirebase():  # test code to send and receive data from the firebase database.
    print ("start of the testFirebase")
    count = 0  # setup the counter
    firebase = dbInitialization()
    a = "No Motion Detected"
    b = "Buzzer is Off"
    if (user != None):  # if authorization is not failed.
        while (1):
            # customize the sensordata before send the data out.
            mq2data = setupMQ2Data(perc["GAS_LPG"],  # mimic LPG data
                                   perc["CO"],  # mimic CO
                                   perc["SMOKE"],  # mimic Smoke
                                   int(time.time()))  # this is the epoch time for this record.

            # customize the sensordata before send the data out.
            bmedata = setupBMEData(bme280.relative_humidity,  # humidity
                                   bme280.pressure,  # pressure
                                   bme280.temperature,  # temp
                                   int(time.time()))  # this is the epoch time for this record.

            if GPIO.input(36) == 1:
                GPIO.output(32, True)
                a = "Motion Detected..."
                b = "Buzzer is On"
                print(a)
                print(b)
                time.sleep(0.5)
                GPIO.output(32, False)

            else:
                GPIO.output(32, False)
                a = "No Motion Detected"
                b = "Buzzer is Off"
                print(a)
                print(b)
                time.sleep(0.5)
            # customize the sensordata before send the data out.
            pirdata = setupPIRData(a,  # mimic LPG data
                                   b,  # mimic Smoke
                                   int(time.time()))  # this is the epoch time for this record.

            sendtoMQ2Firebase(firebase.database(), mq2data)  # save to the public access data tree
            sendtoBMEFirebase(firebase.database(), bmedata)  # save to the public access data tree
            sendtoPIRFirebase(firebase.database(), pirdata)
            sendtoUserFirebase(firebase.database(), mq2data, bmedata, pirdata)
            count += 1;
            sleep(5);
            if (count == 5):  # exit the while loop after 5 times.
                break;
        GetMQ2DatafromFirebase(firebase.database())  # this statement is outside the while loop
        GetBMEDatafromFirebase(firebase.database())  # this statement is outside the while loop
        GetPIRDatafromFirebase(firebase.database())

try:
    print("Press CTRL+C to abort.")

    mq = MQ();
    while True:
        perc = mq.MQPercentage()
        sys.stdout.write("\r")
        sys.stdout.write("\033[K")
        sys.stdout.write("LPG: %g ppm, CO: %g ppm, Smoke: %g ppm" % (perc["GAS_LPG"], perc["CO"], perc["SMOKE"]))
        print("\nTemperature: %0.1f C" % bme280.temperature)
        print("Humidity: %0.1f %%" % bme280.relative_humidity)
        print("Pressure: %0.1f hPa" % bme280.pressure)

        testFirebase()
        sys.stdout.flush()
        time.sleep(0.1)

except:
    GPIO.cleanup()
    print("\nAbort by user")
