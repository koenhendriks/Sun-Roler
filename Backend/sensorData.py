from serial import SerialTimeoutException

from Backend.database import *
from Backend.serialCom import *


class SD:
    """ Read and write sensor values to and from serial device.

    This class provides functions to read data from a serial device and
    to send data to a serial device.

    Attributes:
        port: The port to use to connect to the device.
        baud_rate: The baud rate to use on the connection.
        timeout: The timeout value to use on the connection.

    """

    def __init__(self, port, baud_rate, timeout):
        """ Initialize class with serial connection object, open the serial connection and and create DB object """
        self.ser = SC(port, baud_rate, timeout=timeout)
        self.conn = self.ser.open()
        self.frames = []
        self.db = DB()

    def read_data(self):
        """ Read data from the serial device.

        Data is split up in frames. The frames are being put in a list.
        When five frames are received, extract sensor ID and sensor values from list and convert to integers.
        Insert received values in database.

        Raises:
            ValueError: There has not been any data send from the serial device.
            SerialTimeoutException: A timeout has occurred during read of serial port.

        """
        while 1:
            try:
                frame = self.conn.read()
                try:
                    if frame.hex() != '':
                        self.frames.append(frame.hex())
                    if len(self.frames) == 5:
                        sensor_id = int(self.frames.pop(0), 16)
                        sensor_value = int(''.join(self.frames), 16)
                        n_select = self.db.select_sensor_setting(sensor_id, 'sensor_name')
                        name = n_select[0]["setting_value"]
                        self.db.insert_sensor_value(name, sensor_value)
                        self.control_sunscreens()
                        self.frames.clear()
                except ValueError:
                    # Some frames are empty. Just continue reading frames when this is the case.
                    pass
            except SerialTimeoutException:
                self.conn.log('Timeout has occurred during read of serial port.')

    def send_data(self, data):
        """ Send data to serial device.

        Args:
            data: The data to send to the serial device.

        """
        self.conn.write(data.to_bytes(1, byteorder='big'))

    def control_sunscreens(self):
        """ Check whether sunscreens need to be rolled in or rolled out.

        """
        roll_in = 0
        roll_out = 0
        roll_out_distance = self.db.select_sensor_setting(0, "roll_out_distance")
        roll_in_distance = self.db.select_sensor_setting(0, "roll_in_distance")

        sensors = self.db.select_sensor_ids_names()
        for i in range(0, len(sensors)):
            sensor_id = sensors[i]["sensor"]
            sensor_name = sensors[i]["setting_value"]
            last_reading = self.db.select_last_sensor_value(sensor_name)
            sensor_min_value = self.db.select_sensor_setting(sensor_id, "min_value")
            sensor_max_value = self.db.select_sensor_setting(sensor_id, "max_value")

            if last_reading[0]['sensor_value'] < int(sensor_min_value[0]["setting_value"]):
                roll_in += 1
            elif last_reading[0]['sensor_value'] > int(sensor_max_value[0]["setting_value"]):
                roll_out += 1

        if roll_in == len(sensors):
            self.send_data(int(roll_in_distance[0]['setting_value']))
        elif roll_out >= 1:
            self.send_data(int(roll_out_distance[0]['setting_value']))

sd = SD("COM4", 19200, 0)
sd.read_data()

