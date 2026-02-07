import snap7
from snap7.util import set_int,get_bool, set_bool
import time

client = snap7.client.Client()
client.connect('192.168.0.1', 0, 1)
if client:
    print("Connected ")

read_type = []

def read_int_FromPLC(plc, db_number, start, size):
    Data1 = plc.db_read(db_number, start, size)
    binary_str = ''.join(f'{byte:08b}' for byte in Data1)
    result = int(binary_str, 2)
    print("Integer value: ", result)

def write_int_db(plc, db_number, start, value_tomodify):
    """Write integer value to a PLC DB block."""
    data = bytearray(2)  # Integer takes 2 bytes
    set_int(data, 0, value_tomodify)
    plc.db_write(db_number, start, data)


while True:

    read_int_FromPLC(plc=client, db_number=3, start=22, size=2)
    read_int_FromPLC(plc=client, db_number=3, start=24, size=2)
    read_int_FromPLC(plc=client, db_number=3, start=30, size=2)


    value = input("Value to write in DB (1/0): ")
    if value == 'Q':
        break
    else:
        write_int_db(client, 3, 24, value)
        write_int_db(client, 3, 32, value)

        
    time.sleep(2)
