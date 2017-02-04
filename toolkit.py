import os
import time
import re
import sys
import requests

def download(url,filename=None,path=None,headers=None,proxies=None):
	#copied/changed from http://stackoverflow.com/questions/15644964/python-progress-bar-and-downloads
	print("Starting to download from url:{url}".format(url=url))
	response = requests.get(url, stream=True)
	try:
		totalLength = response.headers.get('content-length')
	except:
		totalLength = None
	if not filename:
		try:
			filename = re.search("filename=([\w._ -]+)",response.headers.get('content-disposition')).group(1).strip('"')
			print("getting filename from response")
		except:
			filename = url.split("/")[-1].strip('"')
			print("grabbing filename from url")
	if path:
		if not os.path.exists(path):
			os.makedirs(path)
		fullFilename = path+filename
	else:
		fullFilename = filename
	print(fullFilename)
	if os.path.isfile(fullFilename):
		resumeByte = os.path.getsize(fullFilename)
		if int(resumeByte) >= int(totalLength):
			return("File already fully downloaded")
		header = {"Range": "bytes={resumeByte}-".format(resumeByte=resumeByte)}
		response = requests.get(url, stream=True,headers=header)
	with open(fullFilename, "ab+") as f:
		start = time.clock()
		if totalLength is None: # no content length header
			f.write(response.content)
		else:
			dl = 0
			if response.status_code == 206:
				print("File already exists, trying to resume (might fail)")
				totalLength = int(totalLength)-int(resumeByte)
			else:
				totalLength = int(totalLength)
			for data in response.iter_content(chunk_size=4096):
				dl += len(data)
				f.write(data)
				done = int(50 * dl / totalLength -1)
				sys.stdout.write("\r[{done}>{todo}] {:.2f}%	kbps:{:.2f}	{doneBytes}/{total}".format(((dl/totalLength)*100),(dl//(time.clock()-start))/1000,done=('='*done),todo=(' '*(50-done)),doneBytes=dl,total=totalLength))
				sys.stdout.flush()
	print("\r\nFile downloaded")
	return({"status":200,"filename":filename,"path":path,"fullFilename":fullFilename})