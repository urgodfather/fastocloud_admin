#!/usr/bin/env python3
import argparse
import os
import sys
from mongoengine import connect
import mysql.connector

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.common.subscriber.login.entry import SubscriberUser
from app.service.service import ServiceSettings

PROJECT_NAME = 'create_provider'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=PROJECT_NAME, usage='%(prog)s [options]')
    parser.add_argument('--mongo_uri', help='MongoDB credentials', default='mongodb://localhost:27017/iptv')
    parser.add_argument('--mysql_host', help='MySQL host', default='localhost')
    parser.add_argument('--mysql_user', help='MySQL username', default='')
    parser.add_argument('--mysql_password', help='MySQL password', default='')
    parser.add_argument('--server_id', help='Server ID', default='')
    parser.add_argument('--country', help='Country', default='US')

    argv = parser.parse_args()
    mysql_host = argv.mysql_host
    mysql_user = argv.mysql_user
    mysql_password = argv.mysql_password
    server_id = argv.server_id
    country = argv.country

    mongo = connect(host=argv.mongo_uri)
    if not mongo:
        sys.exit(1)

    server = ServiceSettings.objects(id=server_id).first()
    if not server:
        sys.exit(1)

    mydb = mysql.connector.connect(
        host=mysql_host,
        user=mysql_user,
        passwd=mysql_password,
        database='xtream_iptvpro'
    )

    mycursor = mydb.cursor(dictionary=True)

    sql = 'SELECT username,password,exp_date,max_connections FROM users'

    mycursor.execute(sql)

    myresult = mycursor.fetchall()

    for sql_entry in myresult:
        new_user = SubscriberUser.make_subscriber(email=sql_entry['username'], password=sql_entry['password'],
                                                  country=country)
        new_user.status = SubscriberUser.Status.ACTIVE
        new_user.add_server(server)
        server.add_subscriber(new_user)

    mydb.close()
