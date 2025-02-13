from mqtt.MQTTClient import MQTTClient

def mqtt_client_process():
    mqtt_client = MQTTClient()
    mqtt_client.run()