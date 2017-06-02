import redis
import numpy
try:
	import xml.etree.cElementTree as ET
except Exception as e:
	import xml.etree.ElementTree as ET

pool = redis.ConnectionPool(host='192.168.0.93',port=6379,db=2)

#load index and map file to redis
def init_to_redis(index_path='data/index.xml',map_path='data/map.txt'):
	index = load_index(index_path)
	maps = load_map(map_path)

	#write index to redis
	try:
		r = redis.Redis(connection_pool=pool)
		if r.lrange("0",0,-1):
			return -1
		pipe = r.pipeline()
		n = 0
		for k in index.keys():
			if index[k]:
				pipe.rpush(k,*index[k])
			n = n + 1
			if n%64==0:
				pipe.execute()
				pipe = r.pipeline()

		r.hmset("maps",maps)
	except Exception as e:
		print e
	return 1

def update_to_redis(index_path='data/index.xml',map_path='data/map.txt'):
	index = load_index(index_path)
	maps = load_map(map_path)

	try:
		r = redis.Redis(connection_pool=pool)
		old_maps = r.hgetall("maps")
		if len(old_maps) < len(maps):
			r.flushdb()
			init_to_redis()
	except Exception as e:
		print e
		return 0
	return 1

def search_by_redis(codes):
	try:
		temp = []
		r = redis.Redis(connection_pool = pool)
		pipe = r.pipeline()
		n = 0
		for code in codes:
			pipe.lrange(code,0,-1)

		for t in pipe.execute():
			temp.extend(t)

		data = []
		pipe = r.pipeline()
		for t in temp:
			pipe.hget("maps",t)

		for t in pipe.execute():
			data.append(t)

	except Exception as e:
		print e
	return list(set(data))

def load_index(index_path='data/index.xml'):
	tree = ET.ElementTree(file=index_path)
	root =  tree.getroot()

	data = {}
	for child in root[0][0]:
		temp = child.attrib
		if temp['images']:
			data[temp['id']] = temp['images'].split(',')
		else:
			data[temp['id']] = []
	return data

def load_map(map_path='data/map.txt'):
	data = {}
	with open(map_path,'rb') as f:
		for line in f:
			temp =line.strip('\n').split("  ")
			data[temp[-1]] = temp[0].split("_")[0]
	return data

def load_codebook(codebook_path='data/codebook.txt'):
	with open(codebook_path,'rb') as f:
		levels = int(f.readline().split('\n')[0])
		k = int(f.readline().split('\n')[0])
		surf_dimensions = int(f.readline().split('\n')[0])
		data = []
		for i in xrange(levels):
			codebook_i = []
			for j in xrange(k):
				s = f.readline().split('\n')[0]
				temp = [numpy.float32(i) for i in s.split(' ')[0:-1]]
				codebook_i.append(temp)
			f.readline()
			data.append(codebook_i)
	data = numpy.array(data)
	return data

def computeNearestIndex(vec,vec_list):
	shortest_dist = numpy.linalg.norm(vec-vec_list[0])
	index = 0
	for l in xrange(1,len(vec_list)):
		d = numpy.linalg.norm(vec-vec_list[l])
		if d < shortest_dist:
			shortest_dist = d
			index = l
	return index

def encode(surfDeses,codebook):
	data = []
	for des in surfDeses:
		temp = []
		for i in xrange(len(codebook)):
			if i > 0:
				des = des - codebook[i-1][temp[i-1]]
			index = computeNearestIndex(des,codebook[i])
			temp.append(index)
		data.append(temp)

	def convert_code(codes,k):
		code = 0
		for i in codes:
			code = i + code*k
		return code

	return [convert_code(codes,len(codebook[0])) for codes in data]

if __name__ == '__main__':
	# load_codebook()
	# load_map()
	# load_index()
	# init_to_redis()
	# print search_by_redis(["1925","1926","2888"])
	update_to_redis()