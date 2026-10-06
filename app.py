#!/usr/bin/env python

# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import random
import time
import sys
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse
import config as config
from BME280SensorSimulator import BME280SensorSimulator
import RPi.GPIO as GPIO
from Adafruit_BME280 import *
import re
from telemetry import Telemetry

# HTTP options
# Because it can poll "after 9 seconds" polls will happen effectively
# at ~10 seconds.
# Note that for scalabilty, the default value of minimumPollingTime
# is 25 minutes. For more information, see:
# https://azure.microsoft.com/documentation/articles/iot-hub-devguide/#messaging
TIMEOUT = 241000
MINIMUM_POLLING_TIME = 9

# messageTimeout - the maximum time in milliseconds until a message times out.
# The timeout period starts at IoTHubClient.send_event_async.
# By default, messages do not expire.
MESSAGE_TIMEOUT = 10000

RECEIVE_CONTEXT = 0
MESSAGE_COUNT = 0
MESSAGE_SWITCH = True
TWIN_CONTEXT = 0
SEND_REPORTED_STATE_CONTEXT = 0
METHOD_CONTEXT = 0
TEMPERATURE_ALERT = 30.0

# global counters
RECEIVE_CALLBACKS = 0
SEND_CALLBACKS = 0
BLOB_CALLBACKS = 0
TWIN_CALLBACKS = 0
SEND_REPORTED_STATE_CALLBACKS = 0
METHOD_CALLBACKS = 0
EVENT_SUCCESS = "success"
EVENT_FAILED = "failed"

# String containing Hostname, Device Id & Device Key in the format:
# "HostName=<host_name>;DeviceId=<device_id>;SharedAccessKey=<device_key>"
telemetry = Telemetry()

CONNECTION_STRING = config.CONNECTION_STRING

def is_correct_connection_string():
    m = re.search("HostName=.*;DeviceId=.*;", CONNECTION_STRING)
    if m:
        return True
    else:
        return False

if not is_correct_connection_string():
    print ( "Device connection string is not correct." )
    telemetry.send_telemetry_data(None, EVENT_FAILED, "Device connection string is not correct.")
    sys.exit(0)

MSG_TXT = "{\"deviceId\": \"Raspberry Pi - Python\",\"temperature\": %f,\"humidity\": %f}"

GPIO.setmode(GPIO.BCM)
GPIO.setup(config.GPIO_PIN_ADDRESS, GPIO.OUT)

def receive_message_callback(message):
    global RECEIVE_CALLBACKS
    print ( "Received Message: %s" % message.data )
    print ( "    Properties: %s" % message.custom_properties )
    RECEIVE_CALLBACKS += 1
    print ( "    Total calls received: %d" % RECEIVE_CALLBACKS )


def device_twin_callback(patch):
    global TWIN_CALLBACKS
    print ( "\nTwin patch received: %s" % patch )
    TWIN_CALLBACKS += 1


def device_method_callback(method_request):
    global METHOD_CALLBACKS, MESSAGE_SWITCH
    print ( "\nMethod callback: methodName = %s, payload = %s" % (method_request.name, method_request.payload) )
    METHOD_CALLBACKS += 1
    response = {"Response": "This is the response from the device"}
    if method_request.name == "start":
        MESSAGE_SWITCH = True
        print ( "Start sending message\n" )
        response = {"Response": "Successfully started"}
    elif method_request.name == "stop":
        MESSAGE_SWITCH = False
        print ( "Stop sending message\n" )
        response = {"Response": "Successfully stopped"}
    client = device_method_callback.client
    client.send_method_response(MethodResponse.create_from_method_request(method_request, 200, response))


def iothub_client_init():
    client = IoTHubDeviceClient.create_from_connection_string(
        CONNECTION_STRING, product_info="HappyPath_RaspberryPi-Python")
    device_method_callback.client = client
    client.on_message_received = receive_message_callback
    client.on_twin_desired_properties_patch_received = device_twin_callback
    client.on_method_request_received = device_method_callback
    client.connect()
    return client


def iothub_client_sample_run():
    client = None
    try:
        client = iothub_client_init()

        print ( "IoTHubClient is reporting state" )
        client.patch_twin_reported_properties({"newState": "standBy"})

        if not config.SIMULATED_DATA:
            sensor = BME280(address = config.I2C_ADDRESS)
        else:
            sensor = BME280SensorSimulator()

        telemetry.send_telemetry_data(parse_iot_hub_name(), EVENT_SUCCESS, "IoT hub connection is established")
        while True:
            global MESSAGE_COUNT, MESSAGE_SWITCH, SEND_CALLBACKS
            if MESSAGE_SWITCH:
                # send a few messages every minute
                print ( "IoTHubClient sending %d messages" % MESSAGE_COUNT )
                temperature = sensor.read_temperature()
                humidity = sensor.read_humidity()
                msg_txt_formatted = MSG_TXT % (
                    temperature,
                    humidity)
                print (msg_txt_formatted)
                message = Message(msg_txt_formatted)
                message.message_id = "message_%d" % MESSAGE_COUNT
                message.correlation_id = "correlation_%d" % MESSAGE_COUNT
                message.custom_properties["temperatureAlert"] = "true" if temperature > TEMPERATURE_ALERT else "false"

                client.send_message(message)
                print ( "Message [%d] sent to IoT Hub." % MESSAGE_COUNT )
                SEND_CALLBACKS += 1
                led_blink()
                MESSAGE_COUNT += 1
            time.sleep(config.MESSAGE_TIMESPAN / 1000.0)

    except KeyboardInterrupt:
        print ( "IoTHubClient sample stopped" )
    except Exception as iothub_error:
        print ( "Unexpected error %s from IoTHub" % iothub_error )
        telemetry.send_telemetry_data(parse_iot_hub_name(), EVENT_FAILED, "Unexpected error %s from IoTHub" % iothub_error)
    finally:
        if client:
            client.shutdown()

def led_blink():
    GPIO.output(config.GPIO_PIN_ADDRESS, GPIO.HIGH)
    time.sleep(config.BLINK_TIMESPAN / 1000.0)
    GPIO.output(config.GPIO_PIN_ADDRESS, GPIO.LOW)

def usage():
    print ( "Usage: iothub_client_sample.py -p <protocol> -c <connectionstring>" )
    print ( "    protocol        : <amqp, amqp_ws, http, mqtt, mqtt_ws>" )
    print ( "    connectionstring: <HostName=<host_name>;DeviceId=<device_id>;SharedAccessKey=<device_key>>" )

def parse_iot_hub_name():
    m = re.search(r"HostName=(.*?)\.", CONNECTION_STRING)
    return m.group(1)

if __name__ == "__main__":
    print ( "\nPython %s" % sys.version )
    print ( "IoT Hub Client for Python" )

    iothub_client_sample_run()
