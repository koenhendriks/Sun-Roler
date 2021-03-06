from serial import SerialException, SerialTimeoutException
from database import DB
from serialCom import SC


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
        """ Initialize class with serial connection object, open the serial connection and create DB object """
        self.ser = SC(port, baud_rate, timeout=timeout)
        self.conn = self.ser.open()
        self.sensor_id = 0
        self.frames = []
        self.db = DB()

    def set_sensor_id(self, sensor_id):
        """ Set the sensor ID instance variable.

        Args:
            sensor_id: The ID of the sensor to use in the instance.

        """
        self.sensor_id = sensor_id

    def get_sensor_id(self):
        """ Get the sensor ID instance variable.

        Returns:
            sensor_id: The ID of the sensor used in the instance.

        """
        return self.sensor_id

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
                    self.set_sensor_id(sensor_id)
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

    def control_sunscreen_manual(self, sensor_id):
        """ Control sunscreen manually.

        Args:
            sensor_id: The ID of the sensor of which to control the sunscreens of.

        """
        roll_out_distance = self.db.select_sensor_setting(0, "roll_out_distance")
        roll_in_distance = self.db.select_sensor_setting(0, "roll_in_distance")

        position_up = self.db.select_sensor_setting(sensor_id, "motor_override_up")
        position_down = self.db.select_sensor_setting(sensor_id, "motor_override_down")

        last_position = self.db.select_last_sensor_value(sensor_id)

        if (position_down[0] == 1) and (last_position[1] == 1):
            self.send_data(int(roll_in_distance[0]))
        elif (position_up[0] == 1) and (last_position[1] == 0):
            self.send_data(int(roll_out_distance[0]))


if __name__ == '__main__':

    # Try to make a connection with the sensors and read the data which is being sent.
    while True:
        try:
            s1 = Control("/dev/ttyUSB0")
            s2 = Control("/dev/ttyUSB1")

        # If connection fails, try to connect again.
        except SerialException:
            continue
        break

    while True:
        s1.read_data()
        s2.read_data()

        # Check if user wants to roll in or roll out the sunscreen manually

        if s1.get_sensor_id() != 0:
            s1.control_sunscreen_manual(s1.get_sensor_id())

        if s2.get_sensor_id() != 0:
            s2.control_sunscreen_manual(s2.get_sensor_id())
