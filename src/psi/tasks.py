from celery import shared_task
from celery.utils.log import get_task_logger
from  concurrent.futures import ThreadPoolExecutor

from django.conf import settings

import requests
import datetime
import threading

from .models import Psi, AirTemperature

logger = get_task_logger(__name__)

URL_PSI = 'https://api.data.gov.sg/v1/environment/psi?date='
URL_AT = 'https://api.data.gov.sg/v1/environment/air-temperature?date='

thread_local = threading.local()


def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session

# @shared_task
def get_psi_data():
    logger.info('Start fetching psi data ...')
    date = datetime.date.today()
    url = URL_PSI + date.strftime('%Y-%m-%d')
    session = get_session()
    with session.get(url) as response:
        json_response = response.json()

        region_metadata = json_response['region_metadata']

        try:
            latest_data = Psi.objects.latest('updated_timestamp')
            items = list(
                filter(lambda x: filter_psi_data(x, latest_data.updated_timestamp), json_response['items']))
        except Exception as e:
            items = json_response["items"]

        psi_list = []
        for region in region_metadata:
            psi_list.append(region['name'])

        for reg in psi_list:
            for item in items:
                psi = Psi.objects.create(region=reg
                                            , updated_timestamp=datetime.datetime.fromisoformat(
                        item['update_timestamp']))
                readings = item.get("readings")
                for k, v in readings.items():
                    if k == "o3_sub_index":
                        psi.o3_sub_index = v[reg]
                    elif k == "pm10_twenty_four_hourly":
                        psi.pm10_twenty_four_hourly = v[reg]
                    elif k == "pm10_sub_index":
                        psi.pm10_sub_index = v[reg]
                    elif k == "co_sub_index":
                        psi.co_sub_index = v[reg]
                    elif k == "pm25_twenty_four_hourly":
                        psi.pm25_twenty_four_hourly = v[reg]
                    elif k == "so2_sub_index":
                        psi.so2_sub_index = v[reg]
                psi.save()
    logger.info('End fetching psi data ...')


# @shared_task
def get_airtemperature_data():
    logger.info('Start fetching AirTemperature data ...')
    date = datetime.date.today()
    url = URL_AT + date.strftime('%Y-%m-%d')
    session = get_session()
    with session.get(url) as response:
        json_response = response.json()

        try:
            latest_data = AirTemperature.objects.latest('timestamp')
            items = list(filter(lambda x: filter_airtemparature_data(x, latest_data.updated_timestamp),
                                json_response['items']))
        except Exception as e:
            items = json_response["items"]

        for item in items:
            readings = item.get('readings')

            for reading in readings:
                if reading['station_id'] == settings.CODE_S100:
                    air_temperature = AirTemperature.objects.create(code=settings.CODE_S100,
                                                                    name="Ang Mo Kio Avenue 5"
                                                                    , timestamp=datetime.datetime.fromisoformat(
                            item['timestamp'])
                                                                    , temperature=reading['value'])
                    air_temperature.save()

    logger.info('End fetching AirTemperature data ...')


def filter_psi_data(raw_data, max_date):
    date = datetime.datetime.fromisoformat(raw_data.get('update_timestamp'))
    return date > max_date


def filter_airtemparature_data(raw_data, max_date):
    date = datetime.datetime.fromisoformat(raw_data.get('timestamp'))
    return date > max_date


@shared_task
def fetch_data():
    tasks = [get_psi_data, get_airtemperature_data]
    with ThreadPoolExecutor() as executor:
        running_tasks = [executor.submit(task) for task in tasks]
        for running_task in running_tasks:
            running_task.result()