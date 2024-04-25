Local TCP client proof-of-concept Python application for the [BristolSEDS](https://bristolseds.co.uk/) entry to the 2024 [UKSEDS Satellite Design Competition](https://hub.ukseds.org/p/competitions-hub). Interactive GUI capable of remotely controlling Raspberry Pi (server), streaming and displaying health, IMU, and 8x8 thermal sensor data. Further development/adaptation of the code possible with many IoT applications, such as remote thermal sensor monitoring over local networks.

![GUI screenshot](https://github.com/CorboPy/sdc_ground_station/assets/137124542/090a8534-f758-460c-8bd8-58432830e1c6 "PrometheusCubeSat.py GUI")

Designed for use with a Pi-based model CubeSat over WiFi.

-> "DATA" requests a complete data packet from the server, updating time, voltage, on-board temp, the Pi's IP, WLAN info, IMU angle, and thermal sensor data, with the potential for additional datas to be collected with further dev.

-> "SHUTDOWN PI" will attempt to shutdown the server.

-> "STREAM ON/OFF" will toggle a $\sim$ 1 second stream of data from the server.

-> "LEFT/RIGHT" are click-and-hold controls originally designed for integration with CubeSat's AOCS subsystem.

-> "IMU Zero Point" calibrates IMU angle data based on desired default CubeSat orientation.

RPi Server Repo: https://github.com/CorboPy/sdc_raspberry_pi

![BristolSEDS_SDC2024patch](https://github.com/CorboPy/sdc_ground_station/assets/137124542/8f2ee752-0c31-44d8-aa2c-7bd7de96d3a2)
