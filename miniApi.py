import requests

class AmazonDrive(object):
	"""This object creates an easy way to map all files and their properties from a shared AmazonDrive link"""
	def __init__(self, shareId):
		if shareId.startswith("http://") or shareId.startswith("https://"):
			shareId = shareId.split("/")[-1]
			shareId = shareId.split("?")[0]
		self.shareId = shareId.strip()
		self.folders = dict()
		self.files = list()
		self.response = str()
		self.responsefolder = str()

	def get(self):
		url = "https://www.amazon.ca/drive/v1/shares/{shareId}?resourceVersion=V2&ContentType=JSON&asset=ALL".format(shareId=self.shareId)
		temp = requests.get(url)
		url = "https://www.amazon.ca/drive/v1/nodes/{ID}/children?resourceVersion=V2&ContentType=JSON&limit=200&sort=%5B%22kind+DESC%22%2C+%22modifiedDate+ASC%22%5D&asset=ALL&tempLink=true&shareId={shareId}".format(ID=temp.json()["nodeInfo"]["id"],shareId=self.shareId)
		temp = requests.get(url)
		folder = temp.json()["data"]
		self.dumpAndReturn(folder)
	
	def dumpAndReturn(self,folder):
			for filee in folder:
				if filee["kind"] == "FOLDER":
					print("folder")
					print(filee["name"])
					self.FolderHandler(filee)
				else:
					print("file")
					self.FileHandler(filee)
	
	def FolderHandler(self,filee):
		url = "https://www.amazon.ca/drive/v1/nodes/{ID}/children?resourceVersion=V2&ContentType=JSON&limit=200&sort=%5B%22kind+DESC%22%2C+%22modifiedDate+ASC%22%5D&asset=ALL&tempLink=true&shareId={shareId}".format(ID=filee["id"],shareId=self.shareId)
		temp = requests.get(url)
		self.folders[filee["id"]] = AmazonSharedFile(filee,self)
		self.dumpAndReturn(temp.json()["data"])
	
	def FileHandler(self,filee):
		self.files.append(AmazonSharedFile(filee,self))

class AmazonSharedFile(object):
	"""folders use the same structure, except for tempLink and contentProperties, which aren't included in folders"""
	def __init__(self, filee,AmazonDriveObj,path=None):
		self.AmazonDriveObj = AmazonDriveObj
		self.protectedFolder = bool(filee["protectedFolder"])
		try:
			self.tempLink = str(filee["tempLink"])
			self.contentProperties = dict(filee["contentProperties"])
			self.path = self.getParentFolder(filee).replace(filee["name"],"")
		except:
			#If a folder is passed into this object, it will trow an exception, because tempLink is not defined
			#if we know it's a folder, we want to create the path to this folder, so we get a nice full path to each folder, so we can use this to place each file in their correct folder
			self.fullpath = self.getParentFolder(filee) + "/"
		self.keywords = list(filee["keywords"])
		self.transforms = list(filee["transforms"])
		self.ownerId = str(filee["ownerId"])
		self.xAccntParentMap = dict(filee["xAccntParentMap"])
		self.eTagResponse = str(filee["eTagResponse"])
		self.id = str(filee["id"])
		self.kind = str(filee["kind"])
		self.xAccntParents = dict(filee["xAccntParents"])
		self.version = int(filee["version"])
		self.labels = list(filee["labels"])
		self.createdDate = str(filee["createdDate"]) #should be date thingy
		self.parentMap = dict(filee["parentMap"])
		self.createdBy = str(filee["createdBy"])
		self.restricted = bool(filee["restricted"])
		self.modifiedDate = str(filee["modifiedDate"]) #should also be date
		self.name = str(filee["name"])
		self.isShared = bool(filee["isShared"]) #Is false if the parent folder is shared, so only when it's directly shared i presume
		self.parents = list(filee["parents"])
		self.status = str(filee["status"])
	def __str__(self):
		return(self.name)
	def __repr__(self):
		return("<AmazonSharedFile {name}>".format(name=self.name))
		
	def getParentFolder(self,filee):
		try:
			if filee["parentMap"]["FOLDER"]:
				for folder in filee["parentMap"]["FOLDER"]:
					path = self.AmazonDriveObj.folders[folder].fullpath + filee["name"]
					return(path)
		except KeyError:
			#First folder will always trow a KeyError, as it tries to lookup the fullpath from a folder it doesn't know
			path = filee["name"]
			return(path)