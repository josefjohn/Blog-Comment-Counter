'''
Created on Mar 18, 2013

@author: JosefJohn
'''
import urllib2
import datetime

months = [1,2,3,4,5]
my_url = 'http://livelearniterate.blogspot.com'
weekly_time_increment = 604800 #seconds
start_of_week = [1359417600, 1360022400, 1360627200, 1361232000, 1361836800,
                 1362441600, 1363046400, 1363651200, 1364256000, 1364860800,
                 1365465600, 1366070400, 1366675200, 1367280000, 1367884800,
                 1368489600] #seconds
posts = set()

#just for checking that the timestamps are at the right time
def print_start_of_week():
    i = 1
    for time in start_of_week:
        print 'week' + str(i) +' = ' + str(datetime.datetime.fromtimestamp(time))
        i+=1   
#print_start_of_week()

#takes a blog url
#returns a set of urls, a url for each post made between jan and may
def get_all_blog_posts(url):
    for month in months:
        url_to_scrape =  url + '/2013_0' + str(month) + '_01_archive.html'
        #get the html from the site
        html = urllib2.urlopen(url_to_scrape)
        for line in html:
            #if the line contains a link to a post
            if (line.find('href=\'http://livelearniterate.blogspot.com/2013/0')> 0):
                #get the beginning of the link
                begin = line.find('<a href=\'http://') + len('<a href=\'')
                #make sure it is a link
                if (line[begin:begin+7] == 'http://'):
                    #get the end of the link
                    end = begin + line[begin:].find('.html\'>') + len('.html')
                    #set the link as the beginning to the end
                    blogpost = line[begin:end]
                    #if the link is not in the set of links, add it
                    if str(blogpost) not in posts:
                        posts.add(str(blogpost))
    return posts

#takes a set of urls that link to blog posts
#returns a list of JSON objects, each object is a dictionary containing a comment
def get_all_comments(set_of_links):
    comments = []
    for link in set_of_links:
        html = urllib2.urlopen(link)
        for line in html:
            #cheating parsing javascript not html
            if ('?showComment' in line and 'var items' in line):
                begin = line.find('var items = [{') + len('var items = [')
                end = line.find('}];') + 1
                users = line[begin:end]
                comments = comments + parse_comments_in_line(users)
    return comments

#takes a comments list and a list of users comments
#adds users to the comments list and returns the comments list
def parse_comments_in_line(users):
    comments = []
    while ('}, {\'id' in users):
        end = users.find('}, {\'id')+1
        user = users[:end]
        comments.append(user)
        users = users[end+2:]
    comments.append(users)
    return comments

def get_comment_details(list_of_comments):
    list_of_dicts = []
    for user in list_of_comments:
        if ('name' in user and 'body' in user):
            comment_start =user.find('body\': ') + len('body\': \'')
            comment_end = user[comment_start:].find('\'')
            comment = user[comment_start:comment_start+comment_end]
            name_start = user.find('{\'name\': ') + len('{\'name\': \'')
            name_end = user[name_start:].find('\'')
            name = user[name_start:name_start+name_end]
            time_start = user.find('timestamp\'') + len('timestamp\': \'')
            time_end = user[time_start:].find('\'')
            time = user[time_start:time_start+time_end]
            print name +':', time + ':', comment
            dict = {}
            dict['name'] = name
            dict['time'] = time
            dict['comment'] = comment
            list_of_dicts.append(dict)
            #print dict
    #print list_of_dicts
    return list_of_dicts

#list_of_comments = get_all_comments(get_all_blog_posts(my_url))
#list_of_dictionaries = get_comment_details(list_of_comments)

