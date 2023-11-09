import wifiConfig

from wifiConfig import WifiConfApp
from swarmnet.logger import Logger

def spawn_wifi_ap() -> None:
  logger = Logger("spawn_wifi_ap")
  logger.info_header("Spawning a WiFi access point")
  
  access_point_config = {"wlan":'wlan0', "inet":None, "ip":'192.168.0.1', "netmask":'255.255.255.0', "ssid":'TestAccessPoint', "password":'1234567890'}
  flask_app_config = {"host":"0.0.0.0", "port":"8080"}
  
  myWifiConfig = wifiConfig.__main__.WifiConfApp(access_point_config, flask_app_config)
  myWifiConfig.start()