import sqlite3
import time


class DB:
    """ Open and close connection with database and manipulate tables and rows in database.

    This class provides functions to open and close a database connection
    and to insert sensor values, settings and log messages.

    """

    def open(self):
        """ Open a connection with the database.

        Returns:
            conn: Database connection object.
            c: Cursor database connection object.

        """
        conn = sqlite3.connect('control_unit.sqlite3')
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
        Insert default roll in and roll out distances and default values for sensor settings.

        """
        conn, c = self.open()  # Specify sensor identification, name, default minimal value and default maximum value.
        sensors = {1: ['anemometer', 0, 0],
                   2: ['rain', 0, 0],
                   3: ['temperature', 20, 25],
                   4: ['humidity', 0, 0],
                   5: ['light', 150, 250]}

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
        insert_values = (0, 'roll_out_distance', 30)
        c.execute("INSERT INTO sensor_settings (sensor, setting_name, setting_value) VALUES (?, ?, ?)",
                  insert_values)

        for key, value in sensors.items():
            c.execute("CREATE TABLE {tn} ({id_fn} {id_ft}, {sv_fn} {sv_ft}, {sp_fn} {sp_ft}, {rt_fn} {rt_ft})"
                      .format(tn=value[0],
                              id_fn='ID', id_ft='INTEGER PRIMARY KEY AUTOINCREMENT',
                              sv_fn='sensor_value', sv_ft='INTEGER',
                              sp_fn='screen_position', sp_ft='INTEGER',
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

        self.close(conn)

    def insert_sensor_value(self, sensor_id, value, screen_pos):
        """ Insert sensor values in database.

        Args:
            sensor_id: ID of sensor to store value of.
            value: Value of reading to store.
            screen_pos: The position of the sunscreen.

        """
        conn, c = self.open()

        sensor_name = self.select_sensor_setting(sensor_id, 'sensor_name')

        insert_values = (value, screen_pos, int(time.time()))
        c.execute("INSERT INTO {s} (sensor_value, screen_position, reading_time) VALUES (?, ?, ?)".format(
            s=sensor_name[0]), insert_values)

        self.close(conn)

    def select_last_sensor_value(self, sensor_id):
        """ Select last sensor value and last known screen position from database.

        Args:
            sensor_id: ID of sensor to select value from.

        """
        conn, c = self.open()

        sensor_name = self.select_sensor_setting(sensor_id, 'sensor_name')

        c.execute("SELECT sensor_value, screen_position FROM {tn} ORDER BY reading_time DESC LIMIT 1".format(
            tn=sensor_name[0]))

        fetched_row = c.fetchone()

        self.close(conn)

        if fetched_row:
            return fetched_row
        else:
            # If no reading found, return zero.
            return [{'sensor_value': 0, 'screen_position': 0}]

    def select_sensor_setting(self, sensor_id, setting_name):
        """ Select setting from sensor_setting table.

        Args:
            sensor_id: ID of sensor.
            setting_name: Name of setting to select value from.

        """
        conn, c = self.open()

        c.execute("SELECT setting_value FROM sensor_settings WHERE sensor = {s} AND setting_name = '{sn}'"
                  .format(s=sensor_id, sn=setting_name))

        fetched_row = c.fetchone()

        self.close(conn)

        return fetched_row

    def insert_log_message(self, message):
        """ Insert log message into database.

        Args:
            message: Message to insert into database.

        """
        conn, c = self.open()

        insert_values = (message, int(time.time()))
        c.execute("INSERT INTO log (message, log_time) VALUES (?, ?)", insert_values)

        self.close(conn)

if __name__ == "__main__":
    # Initialize database when this script is being called directly.
    db = DB()
    db.init()
