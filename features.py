import subprocess
import cv2

'''
extract surf features
'''
class SurfFeatures(object):
	def __init__(self, commandStr='bin/extractSurfFeatures'):
		self.commandStr = commandStr

	'''
	@type train/search
	'''
	def extract(self,kind="train",imagePath='trainImages',\
		featurePath='data/featuresForTrain.txt'):
		if kind in ["train","search","update"]:
			self.commandStr = ' '.join([self.commandStr,kind,imagePath,featurePath])
		elif kind == "old":
			pass
		else:
			print 'args error in extract'
			return -1
		subprocess.call(self.commandStr,shell=True)

	def getSurf(self,imgPath):
		img = cv2.imread(imgPath)
		imgg = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
		surf = cv2.SURF()
		keypoints,descriptors = surf.detectAndCompute(imgg,None,useProvidedKeypoints=False)
		return descriptors

if __name__ == '__main__':
	fe = SurfFeatures()
	# fe.extract()
	print fe.getSurf('data/daily_update/images/Snooker-Video_10121/Snooker-Video_10121-frame127.jpg')