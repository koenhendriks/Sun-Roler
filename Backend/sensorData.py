from serial import SerialException, SerialTimeoutException
from Backend.database import DB
from Backend.serialCom import SC


class SD:
    """ Read and write sensor values to and from serial device.

    This class provides functions to read data from a serial device and
    to send data to a serial device.

    Attributes:
        port: The port to use to connect to the device.
        baud_rate: The baud rate to use on the connection.
        timeout: The timeout value to use on the connection.

    """

    def __init__(self, port, baud_rate, timeout=0):
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
                        sensor_name = n_select[0]["setting_value"]
                        response = self.db.insert_sensor_value(sensor_name, sensor_value)
                        if response == '500':
                            self.conn.log("Couldn't insert sensor value")
                        self.control_sunscreen_auto(sensor_id)
                        self.frames.clear()
                except ValueError:
                    # Some frames are empty. Just continue reading frames when this is the case.
                    pass
            except SerialTimeoutException:
                self.conn.log('Timeout has occurred during read of serial port.')

    def send_data(self, data):
        """ Send data to serial device.

        Encode the data to bytes.

        Args:
            data: The data to send to the serial device.

        """
        try:
            self.conn.write(data.to_bytes(1, byteorder='big'))

        except SerialException:
            self.conn.log("Couldn't control sunscreen.")

    def control_sunscreen_auto(self, sensor_id):
        """ Check whether sunscreen need to be rolled in or rolled out
            and send roll in or roll out distance to control unit.

        Args:
            sensor_id: The ID of the sensor of which to control the sunscreens of.

        """

        roll_out_distance = self.db.select_sensor_setting(0, "roll_out_distance")
        roll_in_distance = self.db.select_sensor_setting(0, "roll_in_distance")

        n_select = self.db.select_sensor_setting(sensor_id, 'sensor_name')
        sensor_name = n_select[0]["setting_value"]

        last_reading = self.db.select_last_sensor_value(sensor_name)

        sensor_min_value = self.db.select_sensor_setting(sensor_id, "min_value")
        sensor_max_value = self.db.select_sensor_setting(sensor_id, "max_value")

        if last_reading[0]['sensor_value'] < int(sensor_min_value[0]["setting_value"]):
            self.send_data(int(roll_in_distance[0]['setting_value']))
        elif last_reading[0]['sensor_value'] > int(sensor_max_value[0]["setting_value"]):
            self.send_data(int(roll_out_distance[0]['setting_value']))

    def control_sunscreen_manual(self, position):
        """ Control sunscreen manually.

        Args:
            position: Indicate whether sunscreen needs to be rolled in or rolled out.
            (zero is roll in and one is roll out)

        """

        roll_out_distance = self.db.select_sensor_setting(0, "roll_out_distance")
        roll_in_distance = self.db.select_sensor_setting(0, "roll_in_distance")

        if position == 0:
            self.send_data(int(roll_in_distance[0]['setting_value']))
        elif position == 1:
            self.send_data(int(roll_out_distance[0]['setting_value']))
