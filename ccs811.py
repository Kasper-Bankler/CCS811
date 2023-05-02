# Import af forskellige libraries herunder ccs811LIBRARY og firebase
import ccs811LIBRARY
import time
import sys
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# JSON filen indeholder den nødvendige information til at oprette forbindelse til firebase (databasen)
cred = credentials.Certificate("serviceAcountKey.json")
# Opretter forbindelse til firebase (database)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Indlæsere sensoren og sætter den i mode 1 (opdatering hvert sek)
sensor = ccs811LIBRARY.CCS811()


def setup(mode=1):
    print('Starter aflæsning af CCS811 ')
    sensor.configure_ccs811()
    sensor.set_drive_mode(mode)

# Checker efter errors
    if sensor.check_for_error():
        sensor.print_error()
        raise ValueError('Fejl med at indlæse sensoren')

    # Henter værdien fra sensoren
    result = sensor.get_base_line()
    sys.stdout.write("Baseline for denne sensor: 0x")

    # Checker om resultatet er mindre end 256 (0x100 i hexadecimal notation)
    if result < 0x100:
        sys.stdout.write('0')
    # Checker om resultatet er mindre end 16 (0x10 i hexadecimal notation)
    if result < 0x10:
        sys.stdout.write('0')
    # Resultatet skrives til konsollen
    sys.stdout.write(str(result) + "\n")


setup(1)  # Setting mode

while True:
    # Hvis sensoren er ledig udskrives CO2 og VOC nivauerne
    if sensor.data_available():
        sensor.read_logorithm_results()
        print("eCO2[%d] TVOC[%d]" % (sensor.CO2, sensor.tVOC))
        # Dataen sendes til firestore (databasen)
        db.collection('data').document('sensor1').update(
            {'co': sensor.CO2, 'voc': sensor.tVOC})
    # Ellers sendes fejlbesked
    elif sensor.check_for_error():
        sensor.print_error()
    # Venter 1 sekund
    time.sleep(1)
