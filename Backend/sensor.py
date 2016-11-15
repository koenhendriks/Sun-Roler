from serial import SerialException, SerialTimeoutException
from Backend.database import DB
from Backend.serialCom import SC


class Control:
    """ Read and write sensor values to and from control unit.

    This class provides functions to read data from a control unit and
    to send data to a control unit.

    Attributes:
        port: The port to use to connect to the device.
        baud_rate: The baud rate to use on the connection.
        timeout: The timeout value to use on the connection.

    """

    def __init__(self, port, baud_rate=19200, timeout=0):
        """ Initialize class with serial connection object, open the serial connection and and create DB object """
        self.ser = SC(port, baud_rate, timeout=timeout)
        self.conn = self.ser.open()
        self.frames = []
        self.db = DB()

    def read_data(self):
        """ Read data from the control unit.

        Data is split up in frames. The frames are being put in a list.
        When five frames are received, extract sensor ID, sunscreen position and sensor values from list
        and convert to integers. Insert received values in database.

        Raises:
            ValueError: There has not been any data send from the control unit.
            SerialTimeoutException: A timeout has occurred during reading of the serial port.

        """
        try:
            frame = self.conn.read()
            try:
                if frame.hex() != '':
                    self.frames.append(frame.hex())
                if len(self.frames) == 6:
                    sensor_id = int(self.frames.pop(0), 16)
                    screen_pos = int(self.frames.pop(0), 16)
                    sensor_value = int(''.join(self.frames), 16)
                    self.db.insert_sensor_value(sensor_id, sensor_value, screen_pos)
                    self.control_sunscreen_auto(sensor_id)
                    self.frames.clear()
            except ValueError:
                # Some frames are empty. Just continue reading frames when this is the case.
                pass
        except SerialTimeoutException:
            self.conn.log('Timeout has occurred during read of serial port.')

    def send_data(self, data):
        """ Send data to control unit.

        Encode the data to bytes and send the data to the control unit.

        Args:
            data: The data to send to the control unit.

        Raises:
            SerialException: Something went wrong during the transfer of data to control unit.

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

        last_reading = self.db.select_last_sensor_value(sensor_id)

        sensor_min_value = self.db.select_sensor_setting(sensor_id, "min_value")
        sensor_max_value = self.db.select_sensor_setting(sensor_id, "max_value")

        if last_reading[0] < int(sensor_min_value[0]):
            if last_reading[1] == 0:
                self.send_data(255)
            else:
                self.send_data(int(roll_in_distance[0]))
        elif last_reading[0] > int(sensor_max_value[0]):
            if last_reading[1] == 1:
                self.send_data(255)
            else:
                self.send_data(int(roll_out_distance[0]))

    def control_sunscreen_manual(self, position):
        """ Control sunscreen manually.

        Args:
            position: Indicate whether sunscreen needs to be rolled in or rolled out.
            (zero is roll in and one is roll out)

        """
        roll_out_distance = self.db.select_sensor_setting(0, "roll_out_distance")
        roll_in_distance = self.db.select_sensor_setting(0, "roll_in_distance")

        if position == 0:
            self.send_data(int(roll_in_distance[0]))
        elif position == 1:
            self.send_data(int(roll_out_distance[0]))

if __name__ == '__main__':
    # Open connections to sensors.
    s1 = Control("COM3")
    s2 = Control("COM4")

    while 1:
        s1.read_data()
        s2.read_data()
