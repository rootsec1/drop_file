import dropbox, os, sys, json

client = dropbox.client.DropboxClient(<your auth token>)
#print 'Linked Account: ',client.account_info()
obj = client.account_info()
username = str(obj['display_name'])
if username.startswith('Abhishek M'):
	username = "Abhishek ($root)"
quota_info = obj['quota_info']
usage = (quota_info['normal']*100)/(quota_info['quota']*1.0)
usage = round(usage,2)
print "\n[+] Signed in as "+username
print "[+] Used approximately "+str(usage)+"% of storage space"

def files_metadata():
	extension = ""
	#print sys.argv
	if len(sys.argv)==3 and sys.argv[2].startswith('*'):
		extension = sys.argv[2]
		extension = extension[(extension.index('.')+1):]
	#print "EXT: "+str(extension)
	folder_metadata = client.metadata('/drop_file/')
	print '[+] Metadata:'
	print '---> Path: '+str(folder_metadata['path'])
	print '---> Size: '+str(folder_metadata['size'])
	tp = folder_metadata['modified'].index('+')
	print '---> Last modified: '+str(folder_metadata['modified'][:tp])
	print '[+] Content:'
	for val in folder_metadata['contents']:
		temp = str(val['path'])
		if len(extension)>0 and not temp.endswith(extension):
			continue
		else:							
			temp = temp[(temp.index('/',2)+1):]
			fileSize = str(val['size'])
			file_format = str(val['mime_type']).title()
			created = str(val['client_mtime'])
			tp = created.index('+')
			print '---> '+temp+'\t'+fileSize+'\t'+file_format+'\t'+created[:tp]

def file_upload(filepath):
	filename = filepath[::-1]
	filename = filename[:(filename.index('/'))]
	filename = filename[::-1]
	directory = filepath[:filepath.index(filename)]

	try:
		if filepath.index('//')>0:
			filepath = filepath[(filepath.index('//')+1):]
			filepath = str(filepath)
	except ValueError as e:
		filepath = str(filepath)

	try:	
		if directory.index('//')>0:
			directory = directory[(directory.index('//')+1):]
			directory = str(directory)
	except ValueError as e:
		directory = str(directory)

	#print "FILEPATH: "+filepath
	#print "FILENAME: "+filename
	#print "DIR: "+str(directory)
	os.chdir(str(directory))
	size = (os.stat(filename).st_size)/1024
	f = open(filename, 'rb')
	print '[\] Uploading '+filepath+' ..\t('+str(size)+' KB)'
	response = client.put_file('/drop_file/'+filename, f)
	print '\n[!] "'+filename+'" file upload successful\n'
	#json.dumps(response)
	files_metadata()

def file_download(filename):
	if filename.startswith('*'):
		extension = filename[(filename.index('.')+1):]
		#print "EXT: "+str(extension)
		folder_metadata = client.metadata('/drop_file/')
		#print "FOLDER_META: "+str(folder_metadata)
		print '\n[\] Downloading all files with extension '+extension+'..'
		for val in folder_metadata['contents']:
			temp = str(val['path'])
			temp = str(temp[(temp.index('/',2)+1):])
			#print "TEMP: "+str(temp)
			if temp.endswith(extension):
				file_download(temp)
	else:
		f,metadata = client.get_file_and_metadata('/drop_file/'+filename)
		out = open(os.getcwd()+'/resources/'+filename,'wb')
		out.write(f.read())
		out.close()
		#print metadata
		print '\n[!] '+filename+' downloaded to '+os.getcwd()+'/resources/'

def main():
	if len(sys.argv)>=2:
		filepath = str(sys.argv[1])
		filesInCurrDir = os.listdir(os.getcwd())
		if filepath=='ls' or filepath=='list':
			files_metadata()
		elif filepath.startswith('download'):
			files_metadata()
			filename = raw_input('\nEnter name of file to download: ')
			if filename=='exit':
				exit()
			file_download(str(filename))
		else:
			if filepath.index('/')<0:
				if filepath in filesInCurrDir:
					filepath = os.getcwd()+'/'+filepath
				else:
					print "[!] Error in filepath. Specify the absolute path stupid "+username
			file_upload(filepath)
	else:
		exit()
	print ''

if __name__ == '__main__':
	main()