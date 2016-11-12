from Backend.database import DB
from serial import SerialException
import serial


class SC:
    """ Create a connection with a serial device on a specified port.

    This class provides functions to open and close a connection with a
    serial device and to log errors occurred during opening and closing
    a connection and reading and writing values to and from the device.

    Attributes:
        port: The port to use to connect to the device.
        baud_rate: The baud rate to use on the connection.
        timeout: The timeout value to use on the connection.

    """

    def __init__(self, port, baud_rate, timeout=0):
        """ Initialize class with serial connection information and create DB object """
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.db = DB()

    def open(self):
        """ Open a serial connection.

        Open a serial connection with a device using the specified parameters.

        Returns:
            Serial object with specified port, baud rate and timeout values.

        Raises:
            SerialException: an error occurred while opening a serial connection.

        """
        try:
            ser = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
            return ser
        except SerialException:
            self.log("An error occurred while opening a serial connection.")

    def close(self, ser):
        """ Close a serial connection.

        Close the serial connection specified in the Serial object parameter.

        Args:
            ser: A Serial object.

        """
        ser.close()

    def log(self, message):
        """ Log errors.

        Log errors occurred while opening and closing a serial connection or while
        reading and writing values to and from the serial device. Messages are being
        inserted in database.

        Args:
            message: The message to log.

        """
        self.db.insert_log_message(message)
