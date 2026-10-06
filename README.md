# IoT Hub Raspberry Pi 3 Client application

> This repo contains the source code to help you get started with Azure IoT using the Microsoft IoT Pack for Raspberry Pi 3 Starter Kit. You will find the [full tutorial on Docs.microsoft.com](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-raspberry-pi-kit-c-get-started).

This repo contains a python application that runs on Raspberry Pi 3 with a BME280 temperature&humidity sensor, and then sends these data to your IoT hub. At the same time, this application receives Cloud-to-Device messages from your IoT hub, and takes actions according to the C2D command.

## Step 1: Set up your Pi
### Enable SSH on your Pi
Follow [this page](https://www.raspberrypi.org/documentation/remote-access/ssh/) to enable SSH on your Pi.

### Enable I2C on your Pi
Follow [this page](https://www.raspberrypi.org/documentation/configuration/raspi-config.md) to enable I2C on your Pi

## Step 2: Connect your sensor with your Pi
### Connect with a physical BME280 sensor and LED
You can follow the image to connect your BME280 and an LED with your Raspberry Pi 3.

![BME280](https://docs.microsoft.com/en-us/azure/iot-hub/media/iot-hub-raspberry-pi-kit-node-get-started/3_raspberry-pi-sensor-connection.png)

### DON'T HAVE A PHYSICAL BME280?
You can use the application to simulate temperature&humidity data and send to your IoT hub.
1. Open the `config.py` file.
2. Change the `SIMULATED_DATA` value from `False` to `True`.

## Step 3: Set up the Python environment

The application uses the [`azure-iot-device`](https://pypi.org/project/azure-iot-device/) SDK (Python 3). Recent Raspberry Pi OS versions block system-wide `pip install` (PEP 668), so use a virtual environment.

1. Install `RPi.GPIO` from the OS packages and clone the application:

   ```
   sudo apt-get install git python3-venv python3-rpi.gpio
   git clone https://github.com/hans-naert/iot-hub-python-raspberrypi-client-app.git
   cd iot-hub-python-raspberrypi-client-app
   ```

2. Create a virtual environment. `--system-site-packages` makes the apt-installed `RPi.GPIO` visible inside it:

   ```
   python3 -m venv --system-site-packages .venv
   source .venv/bin/activate
   ```

3. Install the requirements:

   ```
   pip install -r requirements.txt
   ```

## Step 4: Run your client application

Set your Azure IoT hub device connection string as `CONNECTION_STRING` in `config.py`, then run:

   ```
   .venv/bin/python app.py
   ```

Or, with the virtual environment activated:

   ```
   python app.py
   ```

On first run you are asked whether to send usage data to Microsoft; the answer is stored in `telemetry.config`.

If the application works normally, then you will see the screen like this:

![](./imgs/success.png)

