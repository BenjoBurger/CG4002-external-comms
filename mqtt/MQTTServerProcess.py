from mqtt.MQTTServer import MQTTServer

def mqtt_server_process(visualiser_to_eval_queue):
    mqtt_server = MQTTServer()
    mqtt_server.run()