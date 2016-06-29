try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import json
import datetime
import csv
import time

app_id = "XXXXXXXX" # Keep this a secret
app_secret = "XXXXXXXX" # Keep this a secret
group_id = "413503442030166"

access_token = app_id + "|" + app_secret

#see if the url works and retrives data. If it fails..keep trying again
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

# Handling names and texts which are non english characters
def convert_text_for_csv(text):
	return text.translate({ 0x2019:0x27, 0x201C:0x22, 0x2018:0x27, 0x201D:0x22, 0xa0:0x20 }).encode('utf-8')

def getFacebookPageData(group_id, access_token, number_of_statuses):
    
    # prepare the URL string
    base = "https://graph.facebook.com/v2.6"
    node = "/%s/feed" % group_id 
    fields = "/?fields=message,link,created_time,type,name,id,comments.limit(0).summary(true),shares,reactions.limit(0).summary(true),from"
    parameters = "&limit=%s&access_token=%s" % (number_of_statuses, access_token)
    url = base + node + fields + parameters
    
    # retrieve data
    data = json.loads(get_url_data(url).decode())
    
    return data
    
def getReactionsForGroupStatusPosts(status_id, access_token):
	#refer http://stackoverflow.com/questions/36930414/how-can-i-get-facebook-graph-api-reaction-summary-count-separately/37239851#37239851
    base = "https://graph.facebook.com/v2.6"
    node = "/%s" % status_id
    reactions = "/?fields=" \
    				"reactions.type(LIKE).limit(0).summary(total_count).as(like)" \
    				",reactions.type(LOVE).limit(0).summary(total_count).as(love)" \
    				",reactions.type(WOW).limit(0).summary(total_count).as(wow)" \
    				",reactions.type(HAHA).limit(0).summary(total_count).as(haha)" \
    				",reactions.type(SAD).limit(0).summary(total_count).as(sad)" \
    				",reactions.type(ANGRY).limit(0).summary(total_count).as(angry)"
    parameters = "&access_token=%s" % access_token
    url = base + node + reactions + parameters
    
    # retrieve data
    data = json.loads(get_url_data(url).decode())
    
    return data
    

def processFacebookPageFeedStatus(status, access_token):
    
    status_id = status['id']
    status_message = '' if 'message' not in status.keys() else convert_text_for_csv(status['message'])
    link_name = '' if 'name' not in status.keys() else convert_text_for_csv(status['name'])
    status_type = status['type']
    status_link = '' if 'link' not in status.keys() else convert_text_for_csv(status['link'])
    status_author = convert_text_for_csv(status['from']['name'])
    
    status_published = datetime.datetime.strptime(status['created_time'],'%Y-%m-%dT%H:%M:%S+0000')
    status_published = status_published + datetime.timedelta(hours=-5) 
    status_published = status_published.strftime('%Y-%m-%d %H:%M:%S') 
    
    num_reactions = 0 if 'reactions' not in status else status['reactions']['summary']['total_count']
    num_comments = 0 if 'comments' not in status else status['comments']['summary']['total_count']
    num_shares = 0 if 'shares' not in status else status['shares']['count']

    reactions = getReactionsForGroupStatusPosts(status_id, access_token) if status_published > '2016-02-24 00:00:00' else {}
    
    num_likes = 0 if 'like' not in reactions else reactions['like']['summary']['total_count']
    
    num_likes = num_reactions if status_published < '2016-02-24 00:00:00' else num_likes
    
    num_loves = 0 if 'love' not in reactions else reactions['love']['summary']['total_count']
    num_wows = 0 if 'wow' not in reactions else reactions['wow']['summary']['total_count']
    num_hahas = 0 if 'haha' not in reactions else reactions['haha']['summary']['total_count']
    num_sads = 0 if 'sad' not in reactions else reactions['sad']['summary']['total_count']
    num_angrys = 0 if 'angry' not in reactions else reactions['angry']['summary']['total_count']
    
    # return a tuple of all processed data
    
    return (status_id, status_message, status_author, link_name, status_type, status_link,
           status_published, num_reactions, num_comments, num_shares,  num_likes,
           num_loves, num_wows, num_hahas, num_sads, num_angrys)

def scrapeFacebookGroupFeedStatus(group_id, access_token):
    with open('%s_facebook_statuses.csv' % group_id, 'w') as file:
        w = csv.writer(file)
        w.writerow(["status_id", "status_message", "status_author", "link_name", "status_type", "status_link",
           "status_published", "num_reactions", "num_comments", "num_shares", "num_likes",
           "num_loves", "num_wows", "num_hahas", "num_sads", "num_angrys"])
        
        has_next_page = True
        scrape_starttime = datetime.datetime.now()
        
        print ("Scraping %s Facebook Page: %s\n" % (group_id, scrape_starttime))
        
        statuses = getFacebookPageData(group_id, access_token, 100)
        
        while has_next_page:
            for status in statuses['data']:
            	if 'reactions' in status:            
                	w.writerow(processFacebookPageFeedStatus(status, access_token))
            if 'paging' in statuses.keys():
                statuses = json.loads(get_url_data(statuses['paging']['next']).decode())
            else:
                has_next_page = False
                
        
        print ("\nDone!\n")


if __name__ == '__main__':
	scrapeFacebookGroupFeedStatus(group_id, access_token)
