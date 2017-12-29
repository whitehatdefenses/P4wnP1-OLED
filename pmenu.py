#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import subprocess
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Input pins:
L_pin = 27
R_pin = 23
C_pin = 4
U_pin = 17
D_pin = 22

A_pin = 5
B_pin = 6

GPIO.setmode(GPIO.BCM)

GPIO.setup(A_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(B_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(L_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(R_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(U_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(D_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(C_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up

RST = 24
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
disp.begin()
disp.clear()
disp.display()

width = disp.width
height = disp.height
image = Image.new('1', (width, height))

draw = ImageDraw.Draw(image)
draw.rectangle((0,0,width,height), outline=0, fill=0)

font = ImageFont.load_default()

x = 0
top = -2

def hide_menu():
 draw.rectangle((0,0,width,height), outline=0, fill=0)
 disp.image(image)
 disp.display()

def system_shutdown(max_row,payloads,pos_in_payloads,menu_cursor_pos):
 draw.rectangle((0,0,width,height), outline=0, fill=0)
 draw.text((x, top), "Shutdown P4wnP1",font=font, fill=255)
 draw.text((x, top+24), "to activate payload?",font=font, fill=255)
 draw.text((x, top+48), "Yes / No",font=font, fill=255)
 disp.image(image)
 disp.display()

 try:
  while 1:

   if not GPIO.input(A_pin):
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    disp.image(image)
    disp.display()
    cmd = "sudo shutdown -h now"
    cmdout = subprocess.check_output(cmd, shell = True )

   if not GPIO.input(B_pin):
    draw_menu(max_row,payloads,pos_in_payloads,menu_cursor_pos)

  time.sleep(.18)

 except KeyboardInterrupt:
  GPIO.cleanup() 

def activate_payload(max_row,payloads,pos_in_payloads,menu_cursor_pos):
 # comment out active payload
 cmd = "sed -i -e '/^PAYLOAD=/s/^PAYLOAD=/#PAYLOAD=/' /home/pi/P4wnP1/setup.cfg"
 cmdout = subprocess.check_output(cmd, shell = True )

 # activate payload
 cmd = "sed -i -e '/#PAYLOAD=" + payloads[pos_in_payloads+menu_cursor_pos] + "/s/#PAYLOAD=/PAYLOAD=/' /home/pi/P4wnP1/setup.cfg"
 cmdout = subprocess.check_output(cmd, shell = True )

 system_shutdown(max_row,payloads,pos_in_payloads,menu_cursor_pos)
 
def select_payload(max_row,payloads,pos_in_payloads,menu_cursor_pos):
 draw.rectangle((0,0,width,height), outline=0, fill=0)
 draw.text((x, top), "Activate Payload ?",font=font, fill=255)
 draw.text((x, top+24), payloads[pos_in_payloads+menu_cursor_pos],font=font, fill=255)
 draw.text((x, top+48), "Yes / No",font=font, fill=255)
 disp.image(image)
 disp.display()

 try:
  while 1:
   if not GPIO.input(A_pin):
    activate_payload(max_row,payloads,pos_in_payloads,menu_cursor_pos)
   
   if not GPIO.input(B_pin):
    draw_menu(max_row,payloads,pos_in_payloads,menu_cursor_pos)

  time.sleep(.18)

 except KeyboardInterrupt:
  GPIO.cleanup()

def draw_menu(max_row,payloads,pos_in_payloads,menu_cursor_pos,hidden_menu=0):
 draw.rectangle((0,0,width,height), outline=0, fill=0)
 draw.text((x, top), "Select Payload",font=font, fill=255)
 z = 0
 for i in payloads:
  if z > max_row - 1: # end of screen 
   break
  if z + pos_in_payloads > len(payloads)-1: # end of payload list
   break
  if z == menu_cursor_pos:
   draw.text((x, top+12+(z*8)), ">" + payloads[z+pos_in_payloads],font=font, fill=255)
  else:
   draw.text((x, top+12+(z*8)), " " + payloads[z+pos_in_payloads],font=font, fill=255)
  z += 1
 if hidden_menu > 0:
  hide_menu()
 else:
  disp.image(image)
  disp.display()
 buttons(max_row,payloads,pos_in_payloads,menu_cursor_pos)

# up = menu up, down = menu down, center = select, left = hide menu, right = unhide menu
def buttons(max_row,payloads,pos_in_payloads,menu_cursor_pos):
 try:
  while 1:
   if not GPIO.input(U_pin):
    menu_cursor_pos -= 1

    if menu_cursor_pos < 0: # check if cursor is on top 
     if pos_in_payloads > max_row -1: # check if we not on page 1
      pos_in_payloads -= max_row
      menu_cursor_pos = max_row -1 
     else: # we are on top on page 1
      menu_cursor_pos = 0
 
    draw_menu(max_row,payloads,pos_in_payloads,menu_cursor_pos)

   if not GPIO.input(D_pin):
    if pos_in_payloads + menu_cursor_pos != len(payloads)-1: # check if we are at the end of payloads
      menu_cursor_pos += 1

    if menu_cursor_pos > max_row -1 : # if cursor is at end of screnn jump to next page
     pos_in_payloads += max_row
     menu_cursor_pos = 0

    draw_menu(max_row,payloads,pos_in_payloads,menu_cursor_pos)

   if not GPIO.input(C_pin):
    select_payload(max_row,payloads,pos_in_payloads,menu_cursor_pos)
    
   if not GPIO.input(L_pin):
    hide_menu()
	
   if not GPIO.input(R_pin):
    draw_menu(max_row,payloads,pos_in_payloads,menu_cursor_pos)

   time.sleep(.18)

 except KeyboardInterrupt:
  GPIO.cleanup()

if __name__ == '__main__':
 # get list of payloads
 cmd = "cat /home/pi/P4wnP1/setup.cfg | grep 'PAYLOAD' |  grep -o '^[^#]*#\?[^#]*' | awk -F '=' '{print $2}' | awk -F '.' '{print $1}'"
 cmdout = subprocess.check_output(cmd, shell = True )
 payloads = cmdout.splitlines()
 max_row = 6
 menu_cursor_pos = 0
 pos_in_payloads = 0
 
 draw_menu(max_row,payloads,pos_in_payloads,menu_cursor_pos,1)
