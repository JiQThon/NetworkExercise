import google.oauth2.credentials
import pickle
from urllib import request
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
 
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
CLIENT_SECRETS_FILE = "client_secret.json"
def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_console()
    return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

    # When running locally, disable OAuthlib's HTTPs verification. When
    # running in production *do not* leave this option enabled.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
service = get_authenticated_service()
IDs = []
with open("./YouTuberList.txt",'r') as IDS:
    for line in IDS.readlines():
        IDs.extend(line.strip('\n').split('\t'))

url = 'https://www.youtube.com/channel/{}/videos?view=0&flow=grid'

channel_recent25videos = dict()
for ids in IDs[:20]:
    channel_recent25videos[str(ids)] = list()
    url_id = url.format(ids)
    t = request.urlopen(url_id).read()
    soup = BeautifulSoup(t, 'html.parser')
    for idx in range(3,28):
        channel_recent25videos[ids].append(soup.find_all('h3')[idx].find('a')['href'][9:])

ids = IDs[20]        
channel_recent25videos[str(ids)] = list()
url_id = url.format(ids)
t = request.urlopen(url_id).read()
soup = BeautifulSoup(t, 'html.parser')
for idx in range(3,21):
    channel_recent25videos[ids].append(soup.find_all('h3')[idx].find('a')['href'][9:])
tmp = ['HZ8nhGgdZxY','kQKGI24aydk', 'bJJn1ECjTww', 'cqqb0B5mt2Y', 'LbKcHy9cav0', '9FpXVBg80WM', 'aDCcLQto5BM']
channel_recent25videos[ids].extend(tmp)


url = 'https://www.youtube.com/channel/{}/videos?view=0&flow=grid'

for ids in IDs[21:]:
    channel_recent25videos[str(ids)] = list()
    url_id = url.format(ids)
    t = request.urlopen(url_id).read()
    soup = BeautifulSoup(t, 'html.parser')
    for idx in range(3,28):
        channel_recent25videos[ids].append(soup.find_all('h3')[idx].find('a')['href'][9:])
        
        
 with open('channel_recent25videos.pickle', 'wb') as handle:
    pickle.dump(channel_recent25videos, handle, protocol=pickle.HIGHEST_PROTOCOL)
   
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = "..."

youtube = build(api_service_name, api_version, developerKey = DEVELOPER_KEY)

def get_video_comments(key):
    commentors = dict()
    for video in channel_recent25videos[key]:
        max_iteration = 0

        commentors[video] = list()

        results =youtube.commentThreads().list(part="snippet",maxResults=50,order="time",videoId=video).execute()
        while results:
            if max_iteration >9:
                break
            
            else:
                for item in results['items']:
                    try:
                        comment = item['snippet']['topLevelComment']['snippet']['authorChannelId']['value']
                        commentors[video].append(comment)

                    except KeyError:
                        continue

                # Check if another page exists
                if 'nextPageToken' in results:
                    tmp = results['nextPageToken']
                    results = youtube.commentThreads().list(part="snippet",maxResults=50,pageToken = str(tmp), order="time",videoId=video).execute()
                    max_iteration += 1
                    continue
                else:
                    max_iteration += 10
                    break

    return commentors

def write_to_pickle(key):
    comments = get_video_comments(key)
    name = 'Network_' + str(key)+'.pickle'
    with open(name, 'wb') as handle:
        pickle.dump(channel_recent25videos, handle, protocol=pickle.HIGHEST_PROTOCOL)
