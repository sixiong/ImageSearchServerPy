import subprocess
from features import SurfFeatures
import time
import requests
import pickle
import os
import shutil
import numpy
import util

'''
build RVQ/ERVQ indexs
'''
class Indexs(object):
	def __init__(self, commandStr='bin/buildIndex',
		codebookPath='data/codebook.txt',
		mapFilePath='data/map.txt',
		frameSiftPath='data/tmp/framesiftnum.txt',
		indexFilePath='data/index.xml',
		):
		self.commandStr = commandStr
		self.codebookPath = codebookPath
		self.mapFilePath = mapFilePath
		self.frameSiftPath = frameSiftPath
		self.indexFilePath = indexFilePath
		self.sf = SurfFeatures()
		self.codebook = util.load_codebook()

	def build(self):
		# 1.extract the features of images for search 
		imageSearchPath='/home/hadoop/Snooker/SOQ_Image_Search/Images/New/'
		featureSearchPath='/home/hadoop/Snooker/SOQ_Image_Search/vsurf/New/'
		self.sf.extract(kind="search",imagePath=imageSearchPath,featurePath=featureSearchPath)
		# 2.build index using the fearures
		logFilePath='data/tmp/build_index.log'
		kind = 'build'
		commandStr = ' '.join([self.commandStr,kind,self.codebookPath,featureSearchPath,self.mapFilePath,self.frameSiftPath,self.indexFilePath,logFilePath])
		print commandStr
		subprocess.call(commandStr,shell=True)

	def update(self):
		imageUpdatePath='data/daily_update/images/'
		featureUpdatePath='data/daily_update/features/'
		def getDailyUpdateVideoIds():
			filter_str = "ColumnPrefixFilter('VIDEODATECOME') AND ValueFilter(=,'substring:%s')"%\
			time.strftime("%Y-%m-%d",time.localtime())
			api_url = 'http://192.168.0.68:8003/api/hbase/SNOOKER_VIDEO?filter_str=%s'%filter_str
			r = requests.get(api_url)
			result = [item[0] for item in r.json()]
			return result

		def getVideoImagesById(videoId):
			videoId = "Snooker-Video_" + videoId
			folder_path = imageUpdatePath + videoId.split("-")[1] + "/"
			if not os.path.exists(folder_path):
				os.makedirs(folder_path)
			else:
				shutil.rmtree(folder_path)
				os.makedirs(folder_path)

			api_url = "http://192.168.0.68:8003/api/images/%s"%videoId
			r = requests.get(api_url)
			data = pickle.loads(r.text)

			for k in data.keys():
				with open(folder_path + k.split("-")[2] ,'wb') as f:
					f.write(data[k]['data'])

		def getDailyImages():
			videoIdList = getDailyUpdateVideoIds()
			for videoId in videoIdList:
				getVideoImagesById(videoId)

		# init path
		shutil.rmtree(imageUpdatePath)
		shutil.rmtree(featureUpdatePath)
		os.makedirs(imageUpdatePath)
		os.makedirs(featureUpdatePath)

		# 1. get daily Images from image Server
		getDailyImages()
		# 2.extract the features of images for update
		self.sf.extract(kind="update",imagePath=imageUpdatePath,featurePath=featureUpdatePath)
		# 3.update index using the fearures
		logFilePath='data/tmp/update_index.log'
		kind = "update"
		commandStr = ' '.join([self.commandStr,kind,self.codebookPath,featureUpdatePath,\
			self.mapFilePath,self.frameSiftPath,self.indexFilePath,logFilePath])
		print commandStr
		subprocess.call(commandStr,shell=True)
		# 4.update to redis
		return util.update_to_redis()

	def search(self,imagePath,kind="redis"):
		surfDes = self.sf.getSurf(imagePath)
		codes = util.encode(surfDes,self.codebook)
		if kind == "local":
			indexs = util.load_index()
			videoIds = []
			for code in codes:
				videoIds.extend(indexs[str(code)])
		elif kind == "redis":
			videoIds = util.search_by_redis(codes)
		else:
			videoIds = []
			print "param `kind` error,specify it to `redis` or `local`"
		return videoIds

if __name__ == '__main__':
	indexs = Indexs()
	# indexs.build()
	indexs.update()
	# print indexs.search('data/daily_update/images/Video_10121/frame127.jpg')






