# https://pythonhosted.org/setuptools/setuptools.html#namespace-packages
__import__('pkg_resources').declare_namespace(__name__)

import sys
import logging
import random
import mysql.connector

# https://code.flickr.net/2010/02/08/ticket-servers-distributed-unique-primary-keys-on-the-cheap/

class dbtickets:

    def __init__(self, *hosts, **kwargs):

        self.set_auto_increment = kwargs.get('set_auto_increment', False)

        conns = []

        for cfg in hosts:
            conn = self.connect(**cfg)
            conns.append(conn)

        self.conns = conns

    def connect(self, **cfg):

        if not cfg.get('user', None):
            cfg['user'] = 'dbtickets'

        if not cfg.get('database', None):
            cfg['database'] = 'dbtickets'

        if not cfg.get('host', None):
            cfg['host'] = 'localhost'

        conn = mysql.connector.connect(**cfg)

        if self.set_auto_increment:

            curs = conn.cursor()

            try:

                do_this = [
                    "SET @@auto_increment_increment=2",
                    "SET @@auto_increment_offset=1"
                ]

                for sql in do_this:
                    curs.execute(sql)
                    conn.commit()

            except Exception, e:
                conn.rollback()
                logging.error("failed to %s, because %s" % (sql, e))
                raise Exception, e

        return conn

    def connection(self):

        if len(self.conns) > 1:
            random.shuffle(self.conns)

        return self.conns[0]

    def generate_id(self):

        conn = self.connection()
        curs = conn.cursor()
                    
        sql = "REPLACE INTO Tickets64 (stub) VALUES (%s)"
        params = ('a',)

        try:
            curs.execute(sql, params)
            conn.commit()
        except Exception, e:
            conn.rollback()
            logging.error(e)
            raise Exception, e

        try:
            sql = "SELECT LAST_INSERT_ID()"
            curs.execute(sql)
            
            row = curs.fetchone()
        except Exception, e:
            logging.error(e)
            raise Exception, e

        return row[0]

if __name__ == '__main__':

    cfgs = [
        {'user':'dbtickets', 'password':'PASSWORD', 'host':'HOST', 'database':'dbtickets'}
    ]

    t = dbtickets(*cfgs)
    print t.generate_id()
