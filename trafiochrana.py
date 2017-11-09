# -*- coding: utf-8 -*-
# !/usr/bin/python
import json
import urllib
import time
import random
from math import fabs
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

LAST_SEEN_ = u'lastSeen'
LOCATION_ = u'location'
FUEL_ = u'fuel'
LONGITUDE_ = u'longitude'
LATITUDE_ = u'latitude'
REG_NUMBER_ = u'regNumber'

API_URL = 'https://api.traficar.pl/eaw-rest-api/car?shapeId=5'

cars = {}
last_check = time.gmtime()


def get_data(url):
    response = urllib.urlopen(url)
    response_string = response.read()
    data_file = open('./data/' + current_time() + '.json', 'w')
    data_file.write(response_string)
    data_file.close()
    return json.loads(response_string)


def time_string(time_time):
    return time.strftime("%Y-%m-%d %H:%M:%S", time_time)


def current_time():
    return time_string(time.gmtime())


def log(text):
    print('[%s] %s' % (current_time(), text))


def car_changed(old_entry, car):
    if fabs(old_entry[LATITUDE_] - car[LATITUDE_]) > 0.001 or fabs(old_entry[LONGITUDE_] - car[LONGITUDE_]) > 0.001 or (
                old_entry[FUEL_] != car[FUEL_]):
        return True
    return False


def car_reappeared(old_entry):
    return old_entry[LAST_SEEN_] != time_string(last_check)


def parse_car_data(car_info):
    global last_check
    check_time = time.gmtime()
    returned_cars = car_info[u'cars']
    log('Found cars: %d; all cars in system: %d' % (len(returned_cars), len(cars)))
    for car in returned_cars:
        if car[REG_NUMBER_] in cars:
            old_entry = cars[car[REG_NUMBER_]]
            if car_changed(old_entry, car):
                log(
                    'Car changed. Plates: %s; old lat: %f; new lat: %f; old lon: %f; new lon: %f; old fuel: %d; new fuel: %d; old location: %s; new location: %s; last_seen: %s' % (
                        car[REG_NUMBER_], old_entry[LATITUDE_], car[LATITUDE_], old_entry[LONGITUDE_],
                        car[LONGITUDE_], old_entry[FUEL_], car[FUEL_], old_entry[LOCATION_], car[LOCATION_],
                        old_entry[LAST_SEEN_]))
                cars[car[REG_NUMBER_]][LATITUDE_] = car[LATITUDE_]
                cars[car[REG_NUMBER_]][LONGITUDE_] = car[LONGITUDE_]
                cars[car[REG_NUMBER_]][LOCATION_] = car[LOCATION_]
                cars[car[REG_NUMBER_]][FUEL_] = car[FUEL_]
            elif car_reappeared(old_entry):
                log('Car reappeared. Plates: %s; lat: %f; lon: %f; fuel: %d; location: %s; last seen: %s' % (
                    car[REG_NUMBER_], car[LATITUDE_], car[LONGITUDE_], car[FUEL_], car[LOCATION_],
                    old_entry[LAST_SEEN_]))
            cars[car[REG_NUMBER_]][LAST_SEEN_] = time_string(check_time)
        else:
            log('New car. Plates: %s; lat: %f; lon: %f; fuel: %d; location: %s' % (
                car[REG_NUMBER_], car[LATITUDE_], car[LONGITUDE_], car[FUEL_], car[LOCATION_]))
            cars[car[REG_NUMBER_]] = {
                REG_NUMBER_: car[REG_NUMBER_],
                LATITUDE_: car[LATITUDE_],
                LONGITUDE_: car[LONGITUDE_],
                FUEL_: car[FUEL_],
                LOCATION_: car[LOCATION_],
                LAST_SEEN_: time_string(check_time)
            }
    for key, car in cars.iteritems():
        if car[LAST_SEEN_] == time_string(last_check):
            log('Car disappeared. Plates: %s; lat: %f; lon: %f; fuel: %d; location: %s' % (
                car[REG_NUMBER_], car[LATITUDE_], car[LONGITUDE_], car[FUEL_], car[LOCATION_]))
    last_check = check_time
    sys.stdout.flush()


while True:
    car_info = get_data(API_URL)
    parse_car_data(car_info)
    time.sleep(random.randint(120, 180))
