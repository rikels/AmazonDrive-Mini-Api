import os
import time
import re
import sys
import requests
try:
    from urllib.parse import urlparse,unquote
except ImportError:
     from urlparse import urlparse,unquote


def download(url,filename=None,path=None,headers=None,proxies=None):
    #copied/changed from http://stackoverflow.com/questions/15644964/python-progress-bar-and-downloads
    print("Starting to download from url:{url}".format(url=url))
    response = requests.get(url, stream=True, headers=headers,verify=False)
    try:
        totalLength = response.headers.get('content-length')
    except:
        totalLength = None
    if not filename:
        try:
            filename = unquote(re.search("filename=\"?([\w._ \-&!@#$%~\^\(\)\[\]\+\=\{\}',;`]+)",response.headers.get('content-disposition')).group(1).strip('"'))
            print("got filename from response")
        except:
            filename = unquote(url.split("/")[-1].strip('"'))
            print("created filename from url")
    if path:
        if not os.path.exists(path):
            os.makedirs(path)
        fullFilename = os.path.join(path,filename)
    else:
        path = os.path.abspath(os.path.curdir)
        fullFilename = os.path.join(path,filename)
    print(fullFilename.encode("utf-8"))
    if os.path.isfile(fullFilename):
        resumeByte = os.path.getsize(fullFilename)
        if int(resumeByte) >= int(totalLength):
            print("File already fully downloaded.")
            return({"status":1,"explanation":"Fully downloaded.","filename":filename,"path":path,"fullFilename":fullFilename})
        if headers:
            headers["Range"] = "bytes={resumeByte}-".format(resumeByte=resumeByte)
        else:
            header = {"Range": "bytes={resumeByte}-".format(resumeByte=resumeByte)}
        response = requests.get(url, stream=True,headers=headers,verify=False)
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
            for data in response.iter_content(chunk_size=1024):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / totalLength -1)
                sys.stdout.write("\r[{progress}>{todo}] {percent}%  kbps:{speed}    {doneBytes}/{total}".format(progress=('='*done),todo=(' '*(50-done)),percent=round(((dl/totalLength)*100),2),speed=round(((dl//(time.clock()-start))/1000),2),doneBytes=dl,total=totalLength))
                sys.stdout.flush()
    print("\r\nFile downloaded")
    return({"status":200,"filename":filename,"path":path,"fullFilename":fullFilename})

def downloadStream(filestream,url="leeg",filename=None,path=None,headers=None,proxies=None,forceResume=False):
    #copied/changed from http://stackoverflow.com/questions/15644964/python-progress-bar-and-downloads
    print("Starting to download from url:{url}".format(url=url))
    response = filestream
    try:
        totalLength = response.headers.get('content-length')
    except:
        totalLength = None
    if not filename:
        try:
            filename = re.search("filename=\"?([\w._ \-&!@#$%~\^\(\)\[\]\+\=\{\}',;`]+)",response.headers.get('content-disposition')).group(1).strip('"')
            print("got filename from response")
        except:
            filename = urllparse.unquote(url.split("/")[-1].strip('"'))
            print("created filename from url")
    if path:
        if path.startswith("/"):
            path = path.lstrip("/")
        if not os.path.exists(path):
            os.makedirs(path)
        fullFilename = os.path.join(path,filename)
    else:
        path = os.path.abspath(os.path.curdir)
        fullFilename = os.path.join(path,filename)
    print(fullFilename.encode("utf-8"))
    if os.path.isfile(fullFilename):
        #If the file is partially downloaded we want to resume the download (this is not always possible)
        resumeByte = os.path.getsize(fullFilename)
        if int(resumeByte) >= int(totalLength):
            print("File already fully downloaded.")
            return({"status":1,"explanation":"Fully downloaded.","filename":filename,"path":path,"fullFilename":fullFilename})
        if headers:
            headers["Range"] = "bytes={resumeByte}-".format(resumeByte=resumeByte)
        else:
            headers = {"Range": "bytes={resumeByte}-".format(resumeByte=resumeByte)}
        response = requests.get(url, stream=True,headers=headers,verify=False)
    with open(fullFilename, "ab+") as f:
        start = time.clock()
        if totalLength is None: # no content length header
            f.write(response.content)
        else:
            dl = 0
            #Response code 206 means that the server allows resuming
            if response.status_code == 206:
                print("File already exists, trying to resume (might fail)")
                totalLength = int(totalLength)-int(resumeByte)
            elif forceResume:
                totalLength = int(totalLength)
            #If it isn't possible to resume (status code isn't 206)
            else:
                print("file already exists and the server isn't able to resume the download")
                print("Please delete the file manually to re-download it")
                raise
            for data in response.iter_content(chunk_size=1024):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / totalLength -1)
                sys.stdout.write("\r[{progress}>{todo}] {percent}%  kbps:{speed}    {doneBytes}/{total}".format(progress=('='*done),todo=(' '*(50-done)),percent=round(((dl/totalLength)*100),2),speed=round(((dl//(time.clock()-start))/1000),2),doneBytes=dl,total=totalLength))
                sys.stdout.flush()
    print("\r\nFile downloaded")
    return({"status":200,"filename":filename,"path":path,"fullFilename":fullFilename})