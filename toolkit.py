import os
import time
import re
import sys
import requests

def download(url,filename=None,path=None):
	#copied/changed and added from http://stackoverflow.com/questions/15644964/python-progress-bar-and-downloads
	print("Starting to download from url:{url}".format(url=url))
	response = requests.get(url, stream=True)
	try:
		totalLength = response.headers.get('content-length')
	except:
		totalLength = None
	if not filename:
		try:
			filename = re.search("filename=(.*)",response.headers.get('content-disposition')).group(1).strip('"')
			print("Getting filename from response")
		except:
			filename = url.split("/")[-1].strip('"')
			print("Filename from URL")
	#Checking if the path parameter has been filled
	if path:
		if not os.path.exists(path):
			#If the path doesn't exist, create it recursively.
			os.makedirs(path)
		#Setting the filename to the full path, because the download function will only take a filename
		filename = path+filename
	#Printing the filename, so the user will see where it will be stored
	print(filename)
	#Checking if the file exists, if so, trying to resume download (depends on the host/server)
	if os.path.isfile(filename):
		resumeByte = os.path.getsize(filename)
		if int(resumeByte) >= int(totalLength):
			return("File already fully downloaded")
		#Adding this header will tell the server we want to resume our download
		header = {"Range": "bytes={resumeByte}-".format(resumeByte=resumeByte)}
		response = requests.get(url, stream=True,headers=header)
	with open(filename, "ab+") as f:
		start = time.clock()
		if totalLength is None: # no content length header
			f.write(response.content)
		else:
			dl = 0
			#Response code 206 means that the host/server is able to resume our download
			if response.status_code == 206:
				print("File already exists, host can resume. Trying to resume (this might fail, please delete the file if it doesn't work)")
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
	#Returning a code (can be ignored, but for convenience should be checked)
	return(200)