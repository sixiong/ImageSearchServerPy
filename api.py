import settings
import bottle
from bottle import static_file
from bottle import request, response
from bottle import post, get, put, delete

import time
import os
import pickle
import json
import logging

import indexs
import util

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)s:%(funcName)s] %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',   
)

index = indexs.Indexs()
#
#search video by image
#
@post('/api/image/indexs/search')
def search():
	imageData = request.body.read()
	imagePath = 'data/tmp/query_images/' + str(time.time()).split(".")[0]
	with open(imagePath,'wb') as f:
		f.write(imageData)
	videoIds = index.search(imagePath,"redis")
	os.remove(imagePath)
	response.content_type = 'application/json'
	return {"data":videoIds}

@post('/api/image/indexs/update')
def update():
	return index.update()


if __name__ == '__main__':
	# bottle.run(server='gunicorn', host = settings.api_host, port = settings.api_port,workers=4)
	bottle.run(host = '0.0.0.0', port = 8005)

util.init_to_redis()
app = bottle.default_app()
