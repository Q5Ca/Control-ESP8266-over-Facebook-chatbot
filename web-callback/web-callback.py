from flask import Flask
from flask import request
import requests
import paho.mqtt.client as mqtt
import os
import time

'''
Configuration
 _ACCESS_TOKEN : access token of your app.
 _HUB_VERIFY_TOKEN : Verify token you set.
 _TOPIC : mqtt topic to comunicate with ESP8266.
'''
_ACCESS_TOKEN = ""
_HUB_VERIFY_TOKEN = ""
_TOPIC = ""

'''
Global variables
'''
recipientId = ""
esp_err = None


'''
Functions to communicate with 
'''
def on_connect(mqttc, obj, flags, rc):
	print("Connected to mqtt broker")
def on_message(client, userdata, message):
	global esp_err
	esp_res = str(message.payload.decode("utf-8"))
	if esp_res == "onEd":
		answerMessage(recipientId, u"Đèn led đã bật")
		esp_err = False
	elif esp_res == "offEd":
		answerMessage(recipientId, u"Đèn led đã tắt")
		esp_err = False

mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.connect("localhost", 1883, 60)                        # MQTT broker run on localhost
mqttc.subscribe(_TOPIC, 0)									# Subcribe to topic led

def guiLenh(command):
	global esp_err 
	esp_err = True
	mqttc.publish(_TOPIC, command, qos=2)
	mqttc.loop_start()
	time.sleep(5)
	mqttc.loop_stop()
	if esp_err:
		answerMessage(recipientId, u'Mất kết nối với esp')


'''
Chatbot
'''
app = Flask(__name__)

@app.route("/", methods=['GET'])
def handle_verification():
	if(request.args.get('hub.mode') == "subscribe" and request.args.get('hub.verify_token') == _HUB_VERIFY_TOKEN):      # Check hub verify token
		return request.args.get('hub.challenge')
	else:
		return "not matched"

@app.route("/", methods=['POST'])
def handle_messages():
	req = request.get_json()
	if req["object"] == "page":
		try:
			cmd = str(req['entry'][0]['messaging'][0]['message']['text']).lower()
			global recipientId
			recipientId = str(req['entry'][0]['messaging'][0]['sender']['id'])
			if cmd in[ u'bật', u'bat']:                                                 # Turn LED on
				answerMessage(recipientId, u"Đợi mình 5s")
				guiLenh("on\0")
			elif cmd in [u'tắt', u'tat']:                                               # Turn LED off
				answerMessage(recipientId, u"Đợi mình 5s")
				guiLenh("off\0")
			elif cmd == "hello":
				answerMessage(recipientId, u"Hello")                                    # Answer hello message
			else:
				answerMessage(recipientId,u"Chatbot không hiểu bạn nói gì")             # Default action
				answerMessage(recipientId,u"Mình chỉ biết 2 từ : \"bật\", \"tắt\"")
		except:
			return "OK"
	return "OK" 

def answerMessage(id, message):															# Reply message
	r = requests.post('https://graph.facebook.com/v2.6/me/messages?access_token='+_ACCESS_TOKEN,json={'recipient':{'id': id}, 'message': {'text': message}})
	
if __name__ == "__main__":
	app.run()