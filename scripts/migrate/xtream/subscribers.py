#!/usr/bin/env python3
import os
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.common.subscriber.login.entry import SubscriberUser
from app.common.subscriber.entry import Device
from app.service.service import ServiceSettings

PROJECT_NAME = 'import_subscribers_from_xtream'


def import_subscribers_to_server(db, server: ServiceSettings):
    cursor = db.cursor(dictionary=True)
    sql = 'SELECT username,password,created_at,exp_date FROM users'
    cursor.execute(sql)
    sql_subscribers = cursor.fetchall()

    for sql_entry in sql_subscribers:
        new_user = SubscriberUser.make_subscriber(email=sql_entry['username'], password=sql_entry['password'],
                                                  country='US')
        new_user.status = SubscriberUser.Status.ACTIVE
        created_at = sql_entry['created_at']
        if created_at:
            new_user.created_date = datetime.fromtimestamp(created_at)
        exp_date = sql_entry['exp_date']
        if exp_date:
            new_user.exp_date = datetime.fromtimestamp(exp_date)
        dev = Device(name='Xtream')
        new_user.add_device(dev)
        # save
        new_user.add_server(server)
        server.add_subscriber(new_user)

    cursor.close()