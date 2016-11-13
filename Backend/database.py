from sqlite3 import DatabaseError
import sqlite3
import time


class DB:
    """ Open and close connection with database and manipulate tables and rows in database.

    This class provides functions to open and close a database connection, to insert, select
    and delete sensor values and to insert log messages into the database.

    """

    def json_return(self, c, r):
        """ Return fetched row from SELECT statement in JSON format.

        Taken from: http://www.cdotson.com/2014/06/generating-json-documents-from-sqlite-databases-in-python
        and altered.

        Args:
            c: Cursor object.
            r: Row to manipulate.

        Returns:
            d: JSON formatted data.

        """
        d = {}
        for idx, col in enumerate(c.description):
            d[col[0]] = r[idx]
        return d

    def open(self):
        """ Open a connection with the database.

        Raises:
            DatabaseError: Something went wrong when opening a database connection.

        Returns:
            conn: Database connection object.
            c: Cursor database connection object.
            500: DatabaseError was raised. return error 500

        """
        try:
            conn = sqlite3.connect('control_unit.sqlite3')
            conn.row_factory = self.json_return
            c = conn.cursor()
            return conn, c

        except DatabaseError:
            return '500'

    def close(self, conn):
        """ Close a connection with the database.

        Args:
            conn: Database connection object.

        Raises:
            500: DatabaseError was raised. return error 500

        """
        try:
            conn.commit()
            conn.close()

        except DatabaseError:
            return '500'

    def init(self):
        """ Initialize database.

        Create tables to be able to store log messages, sensor settings and sensor values.
        Insert specified sensor names in table 'sensor_settings' to be able to store sensor settings.
        Insert default roll in and roll out distances.

        Raises:
            DatabaseError: Something went wrong when manipulating the database.

        Returns:
            200: Statements were executed successfully.
            500: DatabaseError was raised. return error 500.

        """
        conn, c = self.open()
        try:
            # Specify sensor identification, name, default minimal value and default maximum value.
            sensors = {1: ['anemometer', 0, 0],
                       2: ['rain', 0, 0],
                       3: ['temperature', 0, 0],
                       4: ['humidity', 0, 0],
                       5: ['light', 0, 0]}

            c.execute("CREATE TABLE {tn} ({id_fn} {id_ft}, {s_fn} {s_ft}, {s_n_fn} {s_n_ft}, {s_v_fn} {s_v_ft})"
                      .format(tn='sensor_settings',
                              id_fn='ID', id_ft='INTEGER PRIMARY KEY AUTOINCREMENT',
                              s_fn='sensor', s_ft='INTEGER',
                              s_n_fn='setting_name', s_n_ft='TEXT',
                              s_v_fn='setting_value', s_v_ft='TEXT'))

            c.execute("CREATE TABLE {tn} ({id_fn} {id_ft}, {m_fn} {m_ft}, {t_fn} {t_ft})"
                      .format(tn='log',
                              id_fn='ID', id_ft='INTEGER PRIMARY KEY AUTOINCREMENT',
                              m_fn='message', m_ft='TEXT',
                              t_fn='log_time', t_ft='INTEGER'))

            # Default roll in distance
            insert_values = (0, 'roll_in_distance', 10)
            c.execute("INSERT INTO sensor_settings (sensor, setting_name, setting_value) VALUES (?, ?, ?)",
                      insert_values)

            # Default roll out distance
            insert_values = (0, 'roll_out_distance', 40)
            c.execute("INSERT INTO sensor_settings (sensor, setting_name, setting_value) VALUES (?, ?, ?)",
                      insert_values)

            for key, value in sensors.items():
                c.execute("CREATE TABLE {tn} ({id_fn} {id_ft}, {sv_fn} {sv_ft}, {rt_fn} {rt_ft})"
                          .format(tn=value[0],
                                  id_fn='ID', id_ft='INTEGER PRIMARY KEY AUTOINCREMENT',
                                  sv_fn='sensor_value', sv_ft='INTEGER',
                                  rt_fn='reading_time', rt_ft='INTEGER'))

                insert_values = (key, 'sensor_name', value[0])
                c.execute("INSERT INTO sensor_settings (sensor, setting_name, setting_value) VALUES (?, ?, ?)",
                          insert_values)

                insert_values = (key, 'min_value', value[1])
                c.execute("INSERT INTO sensor_settings (sensor, setting_name, setting_value) VALUES (?, ?, ?)",
                          insert_values)

                insert_values = (key, 'max_value', value[2])
                c.execute("INSERT INTO sensor_settings (sensor, setting_name, setting_value) VALUES (?, ?, ?)",
                          insert_values)
                return '200'

        except DatabaseError:
            return '500'

        finally:
            self.close(conn)

    def insert_sensor_value(self, sensor_id, value):
        """ Insert sensor values in database.

        Args:
            sensor_id: ID of sensor to store value of.
            value: Value of reading to store.

        Raises:
            DatabaseError: Something went wrong when manipulating the database.

        Returns:
            500: DatabaseError was raised. return error 500.

        """
        conn, c = self.open()
        try:
            sensor_name = self.select_sensor_setting(sensor_id, 'sensor_name')

            insert_values = (value, int(time.time()))
            c.execute("INSERT INTO {s} (sensor_value, reading_time) VALUES (?, ?)".format(
                s=sensor_name[0]["setting_value"]), insert_values)

        except DatabaseError:
            return '500'

        finally:
            self.close(conn)

    def select_last_sensor_value(self, sensor_id):
        """ Select last sensor value from database.

        Args:
            sensor_id: ID of sensor to select value from.

        Raises:
            DatabaseError: Something went wrong when manipulating the database.

        Returns:
            zero: Return sensor_value zero (0) if no rows fetched.
            fetched_rows: The fetched rows from the database containing the sensor value.
            500: DatabaseError was raised. return error 500.

        """
        conn, c = self.open()
        try:
            sensor_name = self.select_sensor_setting(sensor_id, 'sensor_name')

            c.execute("SELECT sensor_value FROM {tn} ORDER BY reading_time DESC LIMIT 1".format(
                tn=sensor_name[0]["setting_value"]))
            fetched_rows = c.fetchall()
            if fetched_rows:
                return fetched_rows
            else:
                # If no reading found, return zero.
                return [{'sensor_value': 0}]

        except DatabaseError:
            return '500'

        finally:
            self.close(conn)

    def select_sensor_values(self, sensor_id, start_time, end_time=''):
        """ Select sensor values from database.

        Args:
            sensor_id: ID of sensor to select values from.
            start_time: Left boundary from time period to return values from.
            end_time: Right boundary from time period to return values from.

        Raises:
            DatabaseError: Something went wrong when manipulating the database.

        Returns:
            fetched_rows: The fetched rows from the database containing the sensor values.
            500: DatabaseError was raised. return error 500.

        """
        conn, c = self.open()
        try:
            # Check if end_time is given or not.
            if not end_time:
                end_time = "''"

            sensor_name = self.select_sensor_setting(sensor_id, 'sensor_name')

            c.execute("SELECT sensor_value FROM {tn} WHERE reading_time BETWEEN {ts} AND {te}".format(
                tn=sensor_name[0]["setting_value"], ts=start_time, te=end_time))
            fetched_rows = c.fetchall()
            return fetched_rows

        except DatabaseError:
            return '500'

        finally:
            self.close(conn)

    def select_sensor_ids_names(self):
        """ Select names and id's from all sensors from database.

        Raises:
            DatabaseError: Something went wrong when manipulating the database.

        Returns:
            fetched_rows: The fetched rows from the database containing the names and the id's of the sensors.
            500: DatabaseError was raised. return error 500.

        """
        conn, c = self.open()
        try:
            c.execute("SELECT sensor, setting_value FROM sensor_settings WHERE setting_name = 'sensor_name'")
            fetched_rows = c.fetchall()
            return fetched_rows

        except DatabaseError:
            return '500'

        finally:
            self.close(conn)

    def delete_sensor_values(self, sensor_id, start_time, end_time=''):
        """ Delete sensor values from database.

        Args:
            sensor_id: ID of sensor to delete values from.
            start_time: Left boundary from time period to delete values from.
            end_time: Right boundary from time period to delete values from.

        Raises:
            DatabaseError: Something went wrong when manipulating the database.

        Returns:
            200: Statements were executed successfully.
            500: DatabaseError was raised. return error 500.

        """
        conn, c = self.open()
        try:
            # Check if end_time is given or not.
            if not end_time:
                end_time = "''"

            sensor_name = self.select_sensor_setting(sensor_id, 'sensor_name')

            c.execute("DELETE FROM {tn} WHERE reading_time BETWEEN {ts} AND {te}".format(
                tn=sensor_name[0]["setting_value"], ts=start_time, te=end_time))
            return '200'

        except DatabaseError:
            return '500'

        finally:
            self.close(conn)

    def select_sensor_setting(self, sensor_id, setting_name):
        """ Select setting from sensor_setting table.

        Args:
            sensor_id: ID of sensor.
            setting_name: Name of setting to select value from.

        Raises:
            DatabaseError: Something went wrong when manipulating the database.

        Returns:
            fetched_rows: The fetched rows from the database containing the sensor setting value.
            500: DatabaseError was raised. return error 500.

        """
        conn, c = self.open()
        try:
            c.execute("SELECT setting_value FROM sensor_settings WHERE sensor = {s} AND setting_name = '{sn}'"
                      .format(s=sensor_id, sn=setting_name))
            fetched_rows = c.fetchall()
            return fetched_rows

        except DatabaseError:
            return '500'

        finally:
            self.close(conn)

    def insert_sensor_setting(self, sensor_id, setting_name, setting_value):
        """ Insert setting into sensor_setting table.

        Args:
            sensor_id: ID of sensor.
            setting_name: Name of setting to select value from.
            setting_value: The value to store.

        Raises:
            DatabaseError: Something went wrong when manipulating the database.

        Returns:
            200: Statements were executed successfully.
            500: DatabaseError was raised. return error 500.

        """
        conn, c = self.open()
        try:
            insert_values = (sensor_id, setting_name, setting_value)
            c.execute("INSERT INTO sensor_settings (sensor, setting_name, setting_value) VALUES (?, ?, ?)",
                      insert_values)
            return '200'

        except DatabaseError:
            return '500'

        finally:
            self.close(conn)

    def update_sensor_setting(self, sensor_id, setting_name, setting_value):
        """ Update setting from sensor_setting table.

        Args:
            sensor_id: ID of sensor.
            setting_name: Name of setting to update value from.
            setting_value: The new value to store.

        Raises:
            DatabaseError: Something went wrong when manipulating the database.

        Returns:
            200: Statements were executed successfully.
            500: DatabaseError was raised. return error 500.

        """
        conn, c = self.open()
        try:
            c.execute("UPDATE sensor_settings SET setting_value = {sv} WHERE setting_name = '{sn}' AND sensor = {s}".format(
                sv=setting_value, sn=setting_name, s=sensor_id))
            return '200'

        except DatabaseError:
            return '500'

        finally:
            self.close(conn)

    def insert_log_message(self, message):
        """ Insert log message into database.

        Args:
            message: Message to insert into database.

        Raises:
            DatabaseError: Something went wrong when manipulating the database.

        Returns:
            200: Statements were executed successfully.
            500: DatabaseError was raised. return error 500.

        """
        conn, c = self.open()
        try:
            insert_values = (message, int(time.time()))
            c.execute("INSERT INTO log (message, log_time) VALUES (?, ?)", insert_values)
            return '200'

        except DatabaseError:
            return '500'

        finally:
            self.close(conn)

    def delete_log_messages(self, start_time, end_time=''):
        """ Delete log messages from database.

        Args:
            start_time: Left boundary from time period to delete values from.
            end_time: Right boundary from time period to delete values from.

        Raises:
            DatabaseError: Something went wrong when manipulating the database.

        Returns:
            200: Statements were executed successfully.
            500: DatabaseError was raised. return error 500.

        """
        conn, c = self.open()
        try:
            # Check if end_time is given or not.
            if not end_time:
                end_time = "''"

            c.execute("DELETE FROM log WHERE log_time BETWEEN {ts} AND {te}".format(
                ts=start_time, te=end_time))
            return '200'

        except DatabaseError:
            return '500'

        finally:
            self.close(conn)

    def select_log_messages(self):
        """ Select all log messages from database.

        Raises:
            DatabaseError: Something went wrong when manipulating the database.

        Returns:
            200: Statements were executed successfully.
            500: DatabaseError was raised. return error 500.

        """
        conn, c = self.open()
        try:
            c.execute("SELECT * FROM log")
            fetched_rows = c.fetchall()
            return fetched_rows

        except DatabaseError:
            return '500'

        finally:
            self.close(conn)

if __name__ == "__main__":
    # Initialize database when this script is being called directly.
    db = DB()
    db.init()
