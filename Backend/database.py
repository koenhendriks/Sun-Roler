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

        Returns:
            conn: Database connection object.
            c: Cursor database connection object.

        """
        conn = sqlite3.connect('control_unit.db')
        conn.row_factory = self.json_return
        c = conn.cursor()
        return conn, c

    def close(self, conn):
        """ Close a connection with the database.

        Args:
            conn: Database connection object.

        """
        conn.commit()
        conn.close()

    def init(self):
        """ Initialize database.

        Create tables to be able to store log messages, sensor settings and sensor values.
        Insert specified sensor names in table 'sensor_settings' to be able to store sensor settings.
        Insert default roll in and roll out distances.

        """
        conn, c = self.open()

        sensors = {1: 'anemometer', 2: 'rain', 3: 'temperature', 4: 'humidity', 5: 'light'}
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

        insert_values = (0, 'roll_in_distance', 10)
        c.execute("INSERT INTO sensor_settings (sensor, setting_name, setting_value) VALUES (?, ?, ?)",
                  insert_values)

        insert_values = (0, 'roll_out_distance', 40)
        c.execute("INSERT INTO sensor_settings (sensor, setting_name, setting_value) VALUES (?, ?, ?)",
                  insert_values)

        for key, value in sensors.items():
            c.execute("CREATE TABLE {tn} ({id_fn} {id_ft}, {sv_fn} {sv_ft}, {rt_fn} {rt_ft})"
                      .format(tn=value,
                              id_fn='ID', id_ft='INTEGER PRIMARY KEY AUTOINCREMENT',
                              sv_fn='sensor_value', sv_ft='INTEGER',
                              rt_fn='reading_time', rt_ft='INTEGER'))

            insert_values = (key, 'min_value', 0)
            c.execute("INSERT INTO sensor_settings (sensor, setting_name, setting_value) VALUES (?, ?, ?)",
                      insert_values)

            insert_values = (key, 'max_value', 0)
            c.execute("INSERT INTO sensor_settings (sensor, setting_name, setting_value) VALUES (?, ?, ?)",
                      insert_values)

            insert_values = (key, 'sensor_name', value)
            c.execute("INSERT INTO sensor_settings (sensor, setting_name, setting_value) VALUES (?, ?, ?)",
                      insert_values)

        self.close(conn)

    def insert_sensor_value(self, sensor, value):
        """ Insert sensor values in database.

        Args:
            sensor: Name of sensor to store value of.
            value: Value of reading to store.

        """
        conn, c = self.open()
        insert_values = (value, int(time.time()))
        c.execute("INSERT INTO {s} (sensor_value, reading_time) VALUES (?, ?)".format(
            s=sensor), insert_values)
        self.close(conn)

    def select_last_sensor_value(self, sensor_name):
        """ Select last sensor value from database.

        Args:
            sensor_name: Name of sensor to select value from.

        Returns:
            zero: Return zero (0) if not rows fetched.
            fetched_rows: The fetched rows from the database containing the sensor value.

        """

        conn, c = self.open()
        c.execute("SELECT sensor_value FROM {tn} ORDER BY reading_time DESC LIMIT 1".format(
            tn=sensor_name))
        fetched_rows = c.fetchall()
        self.close(conn)
        if fetched_rows:
            return fetched_rows
        else:
            # If no reading found, return zero.
            return [{'sensor_value': 0}]

    def select_sensor_values(self, sensor_name, start_time, end_time=''):
        """ Select sensor values from database.

        Args:
            sensor_name: Name of sensor to select values from.
            start_time: Left boundary from time period to return values from.
            end_time: Right boundary from time period to return values from.

        Returns:
            fetched_rows: The fetched rows from the database containing the sensor values.

        """

        # Check if end_time is given or not.
        if not end_time:
            end_time = "''"

        conn, c = self.open()
        c.execute("SELECT sensor_value FROM {tn} WHERE reading_time BETWEEN {ts} AND {te}".format(
            tn=sensor_name, ts=start_time, te=end_time))
        fetched_rows = c.fetchall()
        self.close(conn)
        return fetched_rows

    def select_sensor_ids_names(self):
        """ Select names and id's from all sensors from database.

        Returns:
            fetched_rows: The fetched rows from the database containing the names and the id's of the sensors.

        """
        conn, c = self.open()
        c.execute("SELECT sensor, setting_value FROM sensor_settings WHERE setting_name = 'sensor_name'")
        fetched_rows = c.fetchall()
        self.close(conn)
        return fetched_rows

    def delete_sensor_value(self, sensor_name, start_time, end_time=''):
        """ Delete sensor values from database.

        Args:
            sensor_name: Name of sensor to delete values from.
            start_time: Left boundary from time period to delete values from.
            end_time: Right boundary from time period to delete values from.

        """

        # Check if end_time is given or not.
        if not end_time:
            end_time = "''"

        conn, c = self.open()
        c.execute("DELETE FROM {tn} WHERE reading_time BETWEEN {ts} AND {te}".format(
            tn=sensor_name, ts=start_time, te=end_time))
        self.close(conn)

    def select_sensor_setting(self, sensor_id, setting_name):
        """ Select setting from sensor_setting table.

        Args:
            sensor_id: ID of sensor.
            setting_name: Name of setting to select value from.

        """
        conn, c = self.open()
        c.execute("SELECT setting_value FROM sensor_settings WHERE sensor = {s} AND setting_name = '{sn}'"
                  .format(s=sensor_id, sn=setting_name))
        fetched_rows = c.fetchall()
        self.close(conn)
        return fetched_rows

    def insert_sensor_setting(self, sensor_id, setting_name, setting_value):
        """ Insert setting into sensor_setting table.

        Args:
            sensor_id: ID of sensor.
            setting_name: Name of setting to select value from.
            setting_value: The value to store.

        """
        conn, c = self.open()
        insert_values = (sensor_id, setting_name, setting_value)
        c.execute("INSERT INTO sensor_settings (sensor, setting_name, setting_value) VALUES (?, ?, ?)", insert_values)
        self.close(conn)

    def update_sensor_setting(self, sensor_id, setting_name, setting_value):
        """ Update setting from sensor_setting table.

        Args:
            sensor_id: ID of sensor.
            setting_name: Name of setting to update value from.
            setting_value: The new value to store.

        """
        conn, c = self.open()
        c.execute("UPDATE sensor_settings SET setting_value = {sv} WHERE setting_name = '{sn}' AND sensor = {s}".format(
            sv=setting_value, sn=setting_name, s=sensor_id))
        self.close(conn)

    def insert_log_message(self, message):
        """ Insert log message into database.

        Args:
            message: Message to insert into database.

        """
        conn, c = self.open()
        insert_values = (message, int(time.time()))
        c.execute("INSERT INTO log (message, log_time) VALUES (?, ?)", insert_values)
        self.close(conn)

    def select_log_messages(self):
        """ Select all log messages from database.

        """
        conn, c = self.open()
        c.execute("SELECT * FROM log")
        fetched_rows = c.fetchall()
        self.close(conn)
        return fetched_rows


if __name__ == "__main__":
    # Initialize database when this script is being called directly.
    db = DB()
    db.init()
