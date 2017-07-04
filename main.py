import os
import pygame
import signal
import sys

from time import sleep
import paho.mqtt.client as mqtt

from alarmpanel.button import \
    STATE_DEFAULT, STATE_PRESSED,\
    STATE_1, STATE_2, STATE_3, STATE_4_BAD, STATE_4_GOOD,\
    STATE_ACTIVE, STATE_AVAILABLE
from alarmpanel.ui import UI

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# Configuration -----------------------------------------------------------
# ALARM_PINS should be a comma-separated list of 4 digit pins
PINS = os.environ.get('PINS').split(',')
MQTT_HOST = os.environ.get('MQTT_HOST')
MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))
MQTT_USER = os.environ.get('MQTT_USER')
MQTT_PASS = os.environ.get('MQTT_PASS')
MQTT_CLIENT_ID = os.environ.get('MQTT_CLIENT_ID', 'alarmpanel')
MQTT_STATE_TOPIC = os.environ.get('MQTT_STATE_TOPIC', 'home/alarm')
MQTT_COMMAND_TOPIC = os.environ.get('MQTT_COMMAND_TOPIC', 'home/alarm/set')

pin_input_string = ''
current_state = 'armed_home'
pending_state = ''
connected = False


def on_button_press(n):
    global pin_input_string, client, pending_state

    print n

    # Numeric buttons
    if n < 10:
        pin_input_string = pin_input_string + str(n)
        input_length = len(pin_input_string)
        if input_length == 1:
            btn_input.set_state(STATE_1)
        elif input_length == 2:
            btn_input.set_state(STATE_2)
        elif input_length == 3:
            btn_input.set_state(STATE_3)
        elif input_length == 4:
            if pin_input_string in PINS:
                btn_input.set_state(STATE_4_GOOD)
                update_action_button_states()
            else:
                btn_input.set_state(STATE_4_BAD)

    # Asterisk and pound buttons
    if n == 11 or n == 12:
        # These buttons don't have a purpose yet
        # For now we'll make them clear the input
        clear_input()

    # The "button" showing masked input
    if n == 13:
        clear_input()

    # The three different action buttons
    if n >= 14:
        # Only handle if a correct pin has been entered
        if pin_input_string in PINS:
            if n == 14:
                pending_state = 'disarmed'
                client.publish(MQTT_COMMAND_TOPIC, payload='DISARM', qos=2, retain=True)
            elif n == 15:
                pending_state = 'armed_home'
                client.publish(MQTT_COMMAND_TOPIC, payload='ARM_HOME', qos=2, retain=True)
            elif n == 16:
                pending_state = 'armed_away'
                client.publish(MQTT_COMMAND_TOPIC, payload='ARM_AWAY', qos=2, retain=True)

            clear_input()


def signal_handler(signal, frame):
    print 'got SIGTERM'
    pygame.quit()
    client.loop_stop()
    client.disconnect()
    sys.exit()


def clear_input():
    global pin_input_string
    pin_input_string = ""
    btn_input.set_state(0)
    update_action_button_states()


def update_action_button_states():
    inactive_state = STATE_AVAILABLE if pin_input_string in PINS else STATE_DEFAULT

    print "pending: " + pending_state
    print "state: " + current_state

    btnDisarm.set_state(STATE_ACTIVE if current_state == 'disarmed' or pending_state == 'disarmed' else inactive_state)
    btnArmHome.set_state(STATE_ACTIVE if current_state == 'armed_home' or pending_state == 'armed_home' else inactive_state)
    btnArmAway.set_state(STATE_ACTIVE if current_state == 'armed_away' or pending_state == 'armed_away' else inactive_state)


# Initialization -----------------------------------------------------------
ui = UI('images/bg.png')

# Load all images from the `images` directory
ui.load_images('images')

# Create the two status line elements
status_line_1 = ui.create_status_line((24, 4, 480 - 24, 24))
status_line_2 = ui.create_status_line((24, 34, 480 - 24, 24))
status_line_1.set('Starting up...')

# Create the PIN input buttons
ui.create_button((24, 64, 72, 52), imageFiles={STATE_DEFAULT: '1', STATE_PRESSED: '1_pressed'}, cb=on_button_press, value=1)
ui.create_button((104, 64, 72, 52), imageFiles={STATE_DEFAULT: '2', STATE_PRESSED: '2_pressed'}, cb=on_button_press, value=2)
ui.create_button((184, 64, 72, 52), imageFiles={STATE_DEFAULT: '3', STATE_PRESSED: '3_pressed'}, cb=on_button_press, value=3)
ui.create_button((24, 124, 72, 52), imageFiles={STATE_DEFAULT: '4', STATE_PRESSED: '4_pressed'}, cb=on_button_press, value=4)
ui.create_button((104, 124, 72, 52), imageFiles={STATE_DEFAULT: '5', STATE_PRESSED: '5_pressed'}, cb=on_button_press, value=5)
ui.create_button((184, 124, 72, 52), imageFiles={STATE_DEFAULT: '6', STATE_PRESSED: '6_pressed'}, cb=on_button_press, value=6)
ui.create_button((24, 184, 72, 52), imageFiles={STATE_DEFAULT: '7', STATE_PRESSED: '7_pressed'}, cb=on_button_press, value=7)
ui.create_button((104, 184, 72, 52), imageFiles={STATE_DEFAULT: '8', STATE_PRESSED: '8_pressed'}, cb=on_button_press, value=8)
ui.create_button((184, 184, 72, 52), imageFiles={STATE_DEFAULT: '9', STATE_PRESSED: '9_pressed'}, cb=on_button_press, value=9)
ui.create_button((104, 244, 72, 52), imageFiles={STATE_DEFAULT: '0', STATE_PRESSED: '0_pressed'}, cb=on_button_press, value=0)
ui.create_button((24, 244, 72, 52), imageFiles={STATE_DEFAULT: 'asterisk', STATE_PRESSED: 'asterisk_pressed'}, cb=on_button_press, value=11)
ui.create_button((184, 244, 72, 52), imageFiles={STATE_DEFAULT: 'pound', STATE_PRESSED: 'pound_pressed'}, cb=on_button_press, value=12)

# Create the command buttons
btn_input = ui.create_button((304, 64, 152, 52), imageFiles={STATE_DEFAULT: 'input_empty', STATE_PRESSED: 'input_empty', STATE_1: 'input_1', STATE_2: 'input_2', STATE_3: 'input_3', STATE_4_GOOD: 'input_4_good', STATE_4_BAD: 'input_4_bad'}, cb=on_button_press, value=13)
btnDisarm = ui.create_button((304, 124, 152, 52), imageFiles={STATE_DEFAULT: 'disarm_inactive', STATE_PRESSED: 'disarm_inactive', STATE_AVAILABLE: 'disarm_available', STATE_ACTIVE: 'disarm_active'}, cb=on_button_press, value=14)
btnArmHome = ui.create_button((304, 184, 152, 52), imageFiles={STATE_DEFAULT: 'arm_home_inactive', STATE_PRESSED: 'arm_home_inactive', STATE_AVAILABLE: 'arm_home_available', STATE_ACTIVE: 'arm_home_active'}, cb=on_button_press, value=15)
btnArmAway = ui.create_button((304, 244, 152, 52), imageFiles={STATE_DEFAULT: 'arm_away_inactive', STATE_PRESSED: 'arm_away_inactive', STATE_AVAILABLE: 'arm_away_available', STATE_ACTIVE: 'arm_away_active'}, cb=on_button_press, value=16)

# Draw the screen
ui.update()
sleep(1)


def on_connect(client, userdata, flags, rc):
    global connected, pending_state, status_line_1
    pending_state = ''
    if rc == 0:
        print 'MQTT connection successful'
        status_line_1.set('Connected')
        connected = True
        client.subscribe(MQTT_STATE_TOPIC, 2)
    elif rc == 1:
        print 'MQTT connection refused - incorrect protocol version'
        status_line_1.set('Connection refused - incorrect protocol version')
        connected = False
    elif rc == 2:
        print 'MQTT connection refused - invalid client identifier'
        status_line_1.set('Connection refused - invalid client identifier')
        connected = False
    elif rc == 3:
        print 'MQTT connection refused - server unavailable'
        status_line_1.set('Connection refused - server unavailable')
        connected = False
    elif rc == 4:
        print 'MQTT connection refused - bad username or password'
        status_line_1.set('Connection refused - invalid credentials')
        connected = False
    elif rc == 5:
        print 'MQTT connection refused - not authorized'
        status_line_1.set('Connection refused - not authorized')
        connected = False
    else:
        print 'Unknown connection error: code ' + str(rc)
        status_line_1.set('Unknown connection error: ' + str(rc))
        connected = False


def on_disconnect(client, userdata, rc):
    global connected, status_line_1
    connected = False

    if rc != 0:
        status_line_1.set('Disconnected unexpectedly')


def on_message(client, userdata, message):
    global current_state, pending_state
    current_state = message.payload

    print "received payload: " + current_state

    # HA will send `pending` or `triggered` when the state is about to change
    # In these cases, we can't be 100% sure what the next state will be
    # In all other cases, we definitely know the current state, so wipe out `pending_state`
    if current_state != 'pending' or current_state != 'triggered':
        pending_state = ''

    # Update the corresponding button state
    if current_state == 'disarmed':
        btnDisarm.set_state(STATE_ACTIVE)
    elif current_state == 'armed_home':
        btnArmHome.set_state(STATE_ACTIVE)
    elif current_state == 'armed_away':
        btnArmAway.set_state(STATE_ACTIVE)

    # Update the other button states
    update_action_button_states()

client = mqtt.Client(MQTT_CLIENT_ID)
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.connect_async(MQTT_HOST, MQTT_PORT)

# Main loop ----------------------------------------------------------------
signal.signal(signal.SIGTERM, signal_handler)
ui.update()
client.loop_start()

print "mainloop.."
while True:

    if connected:
        status_line_2.set('Status: ' + current_state)
        ui.process_input()
        ui.update()
    else:
        status_line_2.set('Connecting to MQTT...')
        ui.update()
        client.reconnect()
