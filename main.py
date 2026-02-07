#versin 57648945789 oder so ähnlich

import logging
import requests
import time
import sys
import threading
from flask import *
import os
from smbus import SMBus
from smtplib import SMTP
import math
from flask import jsonify
import json
import smtplib
import logging
from datetime import datetime

#main programm
# I2C simplified: 0x5E
EE895ADDRESS = 0x5E
I2CREGISTER = 0x00

print("                     Kellerbar informationen")
def main():
    '''
    Main program function
    '''
    i2cbus = SMBus(1)
    # delay recommended accoring to this stackoverflow post/wichtig und richtig
    # https://stackoverflow.com/questions/52735862/getting-ioerror-errno-121-remote-i-o-error-with-smbus-on-python-raspberry-w
    time.sleep(1)
    #globale kacke
    global pressure, co2, temperature, co2k, co2kk
    while True:
        try:
            read_data = i2cbus.read_i2c_block_data(EE895ADDRESS, I2CREGISTER, 8)
            # read_data contains ints, which we need to convert to bytes and merge
            # see datasheet
            co2 = read_data[0].to_bytes(1, 'big') + read_data[1].to_bytes(1, 'big')
            temperature = read_data[2].to_bytes(1, 'big') + read_data[3].to_bytes(1, 'big')
            # reserved value - useful to check that the sensor is reading out correctly
            # this should be 0x8000
            resvd = read_data[4].to_bytes(1, 'big') + read_data[5].to_bytes(1, 'big')
            pressure = read_data[6].to_bytes(1, 'big') + read_data[7].to_bytes(1, 'big')

            #co2kalibrierung
            co2k = (int.from_bytes(co2, "big"))
            co2kk = co2k - 120
            #�berpr�fen auf maximal wert AUFPASSEN MIT KALIBRIRUNG max wert ist 5000
            if co2kk > 4879:
                co2kk = "Maximall wert erreicht, mehr als 5000"


            os.system("clear")
            print("                         Kellerbar informationen                      ", zeit)
            print("")
            #print daten
            print("CO2:         ", end='')
            print(co2kk, end='')
            print(" ppm")

            print("Temperature: ", end='')
            print(int.from_bytes(temperature, "big") / 100, end='')
            print(" °C")

#            print("Reserved: ", end='')
#            print(int.from_bytes(resvd, "big"))

            print("Luftdruck:   ", end='')
            print(int.from_bytes(pressure, "big") / 10, end='')
            print(" mbar")

            print("Heizung:     ", end="")
            print(H, "/ 5")
            
            print("Leute:       ", end="")
            print(L)

        except Exception:
            print("Could not read from the sensor. Is it attached?")

        # note the default measurement interval of the sensor is 15 sec/5 für schnellere updates der leute zähler und heizung 
        time.sleep(5)


def req():
    #mach doch hinne alter
    global temp
    time.sleep(2)
    while True:
      try:
         #umwandlung in hex
         temp = (int.from_bytes(temperature, "big") / 100)
         co3 = (int.from_bytes(co2, "big"))
         druck = (int.from_bytes(pressure, "big"))
         druck10 = druck / 10
         #kalibrierung
         co4 = co3 - 120
          #sende den ganzen much
         
         X = requests.get(f"http://meik.bplaced.net/NeueDaten.php?Zeit=&Temperatur={temp}&CO2ppm={co4}&Luftdruck={druck10}".format (temp, co4, druck10))
         time.sleep(600)
      except:
         print("")
         print("connection lost")
         time.sleep(5)



#bissl mathe bissl else if 
def leute():
    global L, LL
    L = "'starting..'"
    LL = 0
    time.sleep(2)
    while True:
            #1min15secsec version (15,45,1min 15sec, ...)
            #wird dadurch schwer ein pro person wert im kopf zu merken aber wofür gibt es logs   print(E, file=open("Leute.txt", "a"))
            coo = (int.from_bytes(co2, "big"))
            z1 = coo
            time.sleep(300)  #1min45
            coo = (int.from_bytes(co2, "big"))
            z2 = coo

            #mathe (immer - das vorletzte)
            D = z2 - z1

            #print("rohdaten:", D, "plus50:", E, file=open("Leute.txt", "a"))
            #print(D, file=open("Longdata.txt", "a"))
      
            #neue methode du wichser
            L =  round(D / 45)
            LL = round(D / 45)


            if L < 0:                 #leute
               L = "'Das Fenster oder Tür ist offen"
            else:
               pass

#temp program
def temp():
    global H
    H = 0
    time.sleep(2)
    while True:
      T = (int.from_bytes(temperature, "big") / 100)
      if T > 26:
         H = 5
      elif T > 24:
         H = 4
      elif T > 21:
         H = 3
      elif T > 17:
           H = 2
      elif T > 15:
           H = 1
      else:
           H = 0
      time.sleep(15)


def ope():
    global zauf
    X = zeit
    zauf = "Kellerbar Offen seit " + zeit

#send mail
def sendmail():
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.application import MIMEApplication
    time.sleep(1)
    f = open("gmail.txt")
    recipient = f.read() #.replace('\n',',')
    f.close()
    #recipient = '["' + recipient + '"]'
    #print(recipient)

    Le = str(L)
    bodyy = "Die Kellerbar ist offen mit ca. " + Le + " Leuten"
    msg = MIMEMultipart()

    msg['Subject'] = 'Kellerbar offen'
    #msg["Body"] = bodyy
    msg['From'] = 'YOUREMAILHERE.com'         ##############################################
    msg['To'] = (', ').join(recipient.split(','))

    msg.attach(MIMEText(bodyy, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('YOUREMAILHERE.com', 'YOUREMAILsmtpAPI')             ##############################################
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(e)
        print("etwas ist schief gelaufen")
        time.sleep(30)
        sendmail()

def check():
     global zauf
     while True:
        if co2k > 2000:
           time.sleep(1)
           threading.Thread(target=sendmail).start()
           threading.Thread(target=ope).start()
           time.sleep(13000)
           if co2k > 2000:
              while True:
                 if co2k > 1300:
                   pass
                 else:
                   zauf = "Kellerbar ist zu"
                   break
                 
           else:
             zauf = "Kellerbar ist zu"
             continue
        else:
             zauf = "Kellerbar ist zu"
             continue

def api():
  time.sleep(3)
  try:
    app = Flask (__name__)
    threading.Thread(target=app.run).start()
    logging.getLogger('werkzeug').disabled = True
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'

    @app.route('/data', methods=['GET'])
    def  home_page():

        return jsonify(
          Zeit=zeit,
          Heizung=H,
          Leute=LL,
          Co2=co2kk,
          Temp=temp,
          Satus=zauf)

    if __name__ == "__main__":
        #thread.start_new_thread(flaskThread, (host=0.0.0.0, port=80, debug=True, use_reloader=False)) #, ssl_context='adhoc', debug=True
        app.run(host="0.0.0.0", port=80, debug=True, use_reloader=False, ssl_context='adhoc')

  except Exception as e:
    print(e)
    time.sleep(3)
    api()

def ct():
   global zeit
   while True:
        t = time.localtime()
        zeit = time.strftime("%H:%M:%S", t)
    
#zauf = [] #debugzauf
#threading auch wichtig und richtig
threading.Thread(target=ct).start()
threading.Thread(target=temp).start()
threading.Thread(target=req).start()
threading.Thread(target=main).start()
threading.Thread(target=leute).start()
threading.Thread(target=api).start()
time.sleep(3)
threading.Thread(target=check).start() #debugzauf / off

#time.sleep(5) #debugzauf
#threading.Thread(target=ope).start() #debugzauf

