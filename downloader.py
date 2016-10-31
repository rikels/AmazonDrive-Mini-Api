import miniApi
import toolkit

#You can pass both, a url from Amazon, or you can pass only the share ID into the AmazonDrive object
urls = ["https://www.amazon.ca/clouddrive/share/oqTnk5GB7EnATDgSTJezVZzrpr0bFZNauWbsr18Ut89","gVlRiNfnJTII64z9H3b4TOQIJXBLaaKfrBSTTQNp0es"]
#This downloader just downloads every file in the shares from the above pasted urls
for url in urls:
	#Creating the object, so we can get workable urls/info back
	tets = miniApi.AmazonDrive(url)
	#Calling the get function, so it will actually gather all info and "return" (store it in it's own variables) it.
	tets.get()
	for filee in tets.files:
		#For each file, pass it to my download function
		toolkit.download(filee.tempLink,path=filee.path)