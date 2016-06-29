try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import json
import datetime
import csv
import time

access_token="XXXXX" #enter your access token

def get_url_data(url):
    req = urllib2.Request(url)
    success = False
    while success is False:
        try: 
            response = urllib2.urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception as e:
            print (e)
            time.sleep(5)
            
            print ("Error for URL %s: %s" % (url, datetime.datetime.now()))

    return response.read()

def convert_text_for_csv(text):
	return text.translate({ 0x2019:0x27, 0x201C:0x22, 0x2018:0x27, 0x201D:0x22, 0xa0:0x20 }).encode('utf-8')

def getFacebookFriendsData(access_token, num_statuses):

    base = "https://graph.facebook.com/v2.6"
    node = "/me/friends" 
    fields = "&fields=first_name,birthday"
    parameters = "/?access_token=%s" % (access_token)
    url = base + node + parameters + fields
    print(url)
    data = json.loads(get_url_data(url).decode())
    
    return data

def processFriendsData(status, access_token):
    
    friend_id = status['id']
    first_name = convert_text_for_csv(status['first_name'])
    birthday = '' if 'birthday' not in status.keys() else status['birthday']
    return (friend_id, first_name, birthday)

def scrapeFriendsData(access_token):
    print("Writing file:")
    with open('my_facebook_statuses.csv', 'w') as file:
        w = csv.writer(file)
        w.writerow(["friend_id", "first_name", "birthday"])
        
        has_next_page = True
        scrape_starttime = datetime.datetime.now()
        
        print ("Scraping Facebook Page: %s\n" % (scrape_starttime))
        
        statuses = getFacebookFriendsData(access_token, 100)
        
        while has_next_page:
            for status in statuses['data']:
                if 'birthday' in status:
                    w.writerow(processFriendsData(status, access_token))
            if 'paging' in statuses.keys():
                statuses = json.loads(get_url_data(statuses['paging']['cursors']['after']).decode())
            else:
                has_next_page = False
                
        
        print ("\nDone!\n")

if __name__ == '__main__':
    scrapeFriendsData( access_token)