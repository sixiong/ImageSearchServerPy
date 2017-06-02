import subprocess
'''
construct RVQ/ERVQ codebooks
'''
class CodeBook(object):
	def __init__(self, commandStr='bin/constructCodebook',
		featurePath='data/featuresForTrain.txt',
		codebookPath='data/codebook.txt'):
		self.commandStr = ' '.join([commandStr,featurePath,codebookPath])
		print self.commandStr

	def construct(self):
		subprocess.call(self.commandStr,shell=True)

if __name__ == '__main__':
	fe = CodeBook()
	fe.construct()