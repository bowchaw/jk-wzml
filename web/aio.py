import pickle
import os
from os import environ
import io
import sys
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
import magic
from google.auth.transport.requests import Request

CLIENT_SECRET_FILE = 'credentials.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']
fid = environ.get('GDRIVE_ID', '')
flag = "NOTDONE"
statement = "NOTDONE"


userinputv2 = sys.argv[1]

def Create_Service(client_secret_file, api_name, api_version, *scopes):
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]

    cred = None

    pickle_file = f'token.pickle'

    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            cred = flow.run_local_server()

        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
        return service
    except Exception as e:
        print('Unable to connect.')
        print(e)
        return None

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES) 

def get_mime_type(file_path):
    m = magic.from_file(file_path, mime=True)
    return m

def filedownload(fileid,pathfile):
  fileid = fileid.replace("/"," ").split()
  fileid= max(fileid, key=len)  
  request = service.files().get_media(fileId=fileid)
  requestt = service.files().get(fileId=fileid, supportsTeamDrives=True)
  response = requestt.execute()
  name = response['name']

  fh = io.BytesIO()
  downloader = MediaIoBaseDownload(fd=fh, request=request)

  done =False
  while not done:
    status, done = downloader.next_chunk()
    #print('Download progress {0}'.format(status.progress() * 100))

  fh.seek(0)  
  with open(pathfile, 'wb') as f:
    f.write(fh.read())
    f.close()
  return name 

def getname(id):
 query = f"parents = '{id}'"
 request = service.files().get_media(fileId=id)
 requestt = service.files().get(fileId=id, supportsTeamDrives=True)
 response = requestt.execute()
 return response['name']

def getfiles(folder_id,name):
 name = name.strip() 
 query = f"parents = '{folder_id}'"
 response = service.files().list(q=query,corpora="allDrives",includeItemsFromAllDrives=True,supportsAllDrives=True,).execute()
 files = response.get('files')
 nextPageToken = response.get("nextPageToken")
 while nextPageToken:
    response = service.files().list(q=query,corpora="allDrives",pageToken=nextPageToken,includeItemsFromAllDrives=True,supportsAllDrives=True).execute()
    files.extend(response.get('files'))
    nextPageToken = response.get("nextPageToken")

 for file in files:
  if "folder" in file['mimeType']:
    if not os.path.exists(os.path.join(name ,file['name'])):
     os.makedirs(os.path.join(name ,file['name']))
    getfiles(file['id'],os.path.join(name ,file['name']))
  else:
    #print("Downloading - " , file['name'] , " | path -", os.path.join(name ,file['name']))
    filedownload(file['id'],os.path.join(name,file['name']))

def download(gdrivelink):
 download_id = gdrivelink.replace("/"," ").split()
 download_id = max(download_id, key=len)
 if "folders" in gdrivelink:
  orgname = getname(download_id) 
  if not os.path.exists(orgname):
     os.makedirs(orgname)
  getfiles(download_id,orgname)
  flag = "Downloaded : "+ getname(download_id)
 else:
  filedownload(download_id,getname(download_id))
  flag = "Downloaded : "+ getname(download_id)
 return flag  

def createfolder(folderpath , cf):
 tests = [folderpath]
 for test in tests:
    file_metadata = {
        'name': test,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [cf]
    }
 h = service.files().create(body=file_metadata, supportsAllDrives=True).execute()
 id = h['id']
 flag = "DONE"
 return id

def upload(path, folder): 
 global flag , statement    
 if os.path.isdir(path):
    base = os.path.basename(path)
    folder_id = createfolder(base, folder)
    if flag=="NOTDONE": 
     statement = "https://drive.google.com/drive/folders/" + folder_id
     flag = 'DONE'
    filenames = os.listdir(path)
    for filename in os.listdir(path):  
      file = os.path.join(path, filename)
      upload(file, folder_id)
 else:   
    filenames = [path]
    ff = folder
    for filename in filenames:
      file = filename
    mime = get_mime_type(file)
    file_metadata = {
        'name': os.path.basename(filename),
        'mimeType': mime,
        'parents': [ff]
    }
    media = MediaFileUpload(file, mimetype=mime, resumable=True,
                                     chunksize=50 * 1024 * 1024)
    done = service.files().create(body=file_metadata, media_body=media, fields='id', supportsAllDrives=True).execute()
    finallink = done['id']
    if flag=="NOTDONE": 
     statement = "https://drive.google.com/uc?id="+ finallink + "&export=download"
     flag = 'DONE'

def gdrive(object):
 global fid  
 upload(object, fid)
 return statement

def allprocess(input):
 codeoutput = ""   
 if "drive.google.com" in input:
  codeoutput = download(input)
  return codeoutput
 else:
  codeoutput = gdrive(input)
  return codeoutput


output = allprocess(userinputv2)
print(output)    
