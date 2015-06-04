# Listof used libraries################ 
########################################
#!/usr/bin/python
import urllib2
import urllib
import platform
import sys
import os
import struct
import time
import usb.core
import usb.util
import usb.backend.libusb0 as libusb0
from PIL import Image, ImageFont, ImageDraw
import string
from bitarray import bitarray
#########################################
# Parameters

MAX_PRINTER_DOTS_PER_LINE = 384
SET_FONT_MODE_3 = b'\x1b!\x08'
SELECT_SDL_GRAPHICS = b'\x1b*\x08'
DOTS_PER_LINE = 384
BYTES_PER_DOT_LINE = DOTS_PER_LINE/8
SET_DARKNESS_LIGHT = b'\x1bX\x42\x50'
RESTORE_DARKNESS = b'\x1bX\x42\x55'

# Status Bits and Enquire

FEED_PAST_CUTTER = b'\n' *5 #size of the printing 
USB_BUSY = 66
ENQUIRE_STATUS = b'\x1d\x05'

HEAD_UP = 1
MECHANISM_RUNNING = 2
BUFFER_EMPTY = 4
PAPER_OUT = 8
RESERVED = 16
SPOOLING = 32
ERROR = 64
ALWAYS_SET = 128

# Printer identification
PIPSTA_USB_VENDOR_ID = 0x0483
PIPSTA_USB_PRODUCT_ID = 0xA053

# subroutine to connect o the site using basic authentication, if it requires password it 
# returns a error messagem.
def web():
  	handle = 'a'
  	url = 'http://openorder.eu01.aws.af.cm/printjob.php?key=12345&printercode=1'
    	req = urllib2.Request(url)
    	try:
            handle = urllib2.urlopen(req).read()
    	except IOError, e:
     	   if hasattr(e,'code'):
             if e.code != 401:   #in case it is not a basic digest authentication
          	print 'error'
          	print e.code
       	     else:
                handle = e.headers

  	return handle
# verify if the printer is connected and if the end point is reachble 
def connect():

    if sys.version_info[0] != 2:
         sys.exit
    if platform.system() != 'Linux':
        sys.exit

    # Find the Pipsta's specific Vendor ID and Product ID
    dev = usb.core.find(idVendor=PIPSTA_USB_VENDOR_ID,
                        idProduct=PIPSTA_USB_PRODUCT_ID,
                        backend=libusb0.get_backend())                       

    if dev is None:  # if no such device is connected...
        raise IOError  # ...report error

    try:
       
        dev.reset()

        dev.set_configuration()
    except usb.core.USBError as ex:
        os.system ('sudo shutdown -r now')
    except AttributeError as ex:
        os.system ('sudo shutdown -r now')

    cfg = dev.get_active_configuration()  # Get a handle to the active interface

    interface_number = cfg[(0, 0)].bInterfaceNumber
    usb.util.claim_interface(dev, interface_number)
    alternate_setting = usb.control.get_interface(dev, interface_number)
    interface = usb.util.find_descriptor(
        cfg, bInterfaceNumber=interface_number,
        bAlternateSetting=alternate_setting)

    ep_out = usb.util.find_descriptor(
        interface,
        custom_match=lambda e:
        usb.util.endpoint_direction(e.bEndpointAddress) ==
        usb.util.ENDPOINT_OUT
    )

    ep_in = usb.util.find_descriptor(
        interface,
        custom_match=lambda e:
        usb.util.endpoint_direction(e.bEndpointAddress) ==
        usb.util.ENDPOINT_IN
    )
    return(dev, ep_out, ep_in)

def convert_image():
    file_in = 'logo.png'
    img = Image.open(file_in)
    wpercent = (312/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    img = img.resize((384, hsize), Image.ANTIALIAS)
    
    imagebits = bitarray(img.getdata(), endian='big')
    imagebits.invert()
    return imagebits.tobytes()


def print_image(device, usb_out, data):
    
      try:    
         usb_out.write(SET_DARKNESS_LIGHT)
         usb_out.write(SET_FONT_MODE_3)
         cmd = struct.pack('3s2B', SELECT_SDL_GRAPHICS,
                      (DOTS_PER_LINE/8) & 0xFF,
                      (DOTS_PER_LINE/8) / 256)
         lines = len(data)//BYTES_PER_DOT_LINE
         start = 0
         for line in range (0, lines):
            start = line*BYTES_PER_DOT_LINE
            end = start + BYTES_PER_DOT_LINE
            usb_out.write(b''.join([cmd, data[start:end]]))
            res = device.ctrl_transfer(0xC0, 0x0E, 0x020E, 0, 2)
            while res[0] == USB_BUSY:
              time.sleep(0.01)
              res = device.ctrl_transfer(0xC0, 0x0E, 0x020E, 0, 2)
      finally:
          usb_out.write(RESTORE_DARKNESS)
def main():
    b = 'a'
    dev, ep_out, ep_in = connect()
    if ep_out is None:
       raise IOError('missing end point')
    if ep_in is None:
       raise IOError('missing end point')
   

    
    ep_out.write(b'\x1b!\x00')
    
    # prints whetever the txt varible contains 
    while 1:    
  
       txt = web()
       a = len(txt)
       if ((a < 2) or (txt == b)):    
            time.sleep(1)
            continue
       else:
            b = txt
            dev, ep_out, ep_in = connect()
            ep_out.write(b'\x1b!\x00')
            for x in txt:
               ep_out.write(x)    # write all the data to the usb OUT endpoint
               res = dev.ctrl_transfer(0xC0, 0x0E, 0x020E, 0, 2)
               while res[0] == USB_BUSY:
                  time.sleep(0.01)
                  res = dev.ctrl_transfer(0xC0, 0x0E, 0x020E, 0, 2)
      
            print_data = convert_image()
            print_image(dev, ep_out, print_data)  
            ep_out.write(FEED_PAST_CUTTER)


            ep_out.write(ENQUIRE_STATUS)                
            response = ep_in.read(1)
  
        # the following functions make the system wait for the buffer to be empty
        
            while((response[0] & BUFFER_EMPTY)==0):
                 ep_out.write(ENQUIRE_STATUS)
                 response = ep_in.read(1)
                 time.sleep(0.1)
       
            while(response[0] & MECHANISM_RUNNING):
                 ep_out.write(ENQUIRE_STATUS)
                 response = ep_in.read(1)
                 time.sleep(0.1)


            usb.util.dispose_resources(dev)
            time.sleep(40)
          
if __name__ == '__main__':
    main()

