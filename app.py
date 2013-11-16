from g15daemon import g15screen
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import requests
import time

# Config options

MAX_X=160
MAX_Y=43

CURRENCIES = ['BTCUSD', 'BTCPLN', 'BTCRMB']

c_index = 0

# Plugin content

def get_frame():
	r = requests.get('http://data.mtgox.com/api/2/'+CURRENCIES[c_index]+'/money/ticker')
	data = r.json()

	text = "H: " + data['data']['high']['display']

	font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf", 24)


	image = Image.new("RGBA", (160,43), (255,255,255))
	d_usr = ImageDraw.Draw(image)

	text = "High: " + data['data']['high']['display']
	d_usr.text((0,0), text,(0,0,0))
	
	text = "Low:  " + data['data']['low']['display']
	d_usr.text((0,10), text,(0,0,0))
	
	text = "Buy:  " + data['data']['high']['display']
	d_usr.text((0,20), text,(0,0,0))
	
	text = "Sell: " + data['data']['high']['display']
	d_usr.text((0,30), text,(0,0,0))
	
	text = data['data']['last_local']['display']
	d_usr.text((77,7), text,(0,0,0), font=font)

	return image


# Display bitmap

g15=g15screen(0)

while 1:
	g15.clear()
	image = get_frame()
	for y in range(MAX_Y):
	    for x in range(MAX_X):
	    	if image.getpixel((x, y)) != (255,255,255,255):
	        	g15.set_pixel(x,y, chr(1))


	g15.display()
	time.sleep(1)
