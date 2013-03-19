'''
Created on Mar 18, 2013

@author: JosefJohn
'''
import urllib2
import json

months = [1,2,3,4,5]
my_url = 'http://livelearniterate.blogspot.com'

posts = set()

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

#partially working, only returns 1 comment from each post even if there are more than 1!!!!!!!!!!!!
#takes a set of urls that link to blog posts
#returns a list of JSON objects, each object is a dictionary containing a comment
def get_all_comments(set_of_links):
    comments = []
    for link in set_of_links:
        #print link
        html = urllib2.urlopen(link)
        for line in html:
            if ('?showComment' in line):
                begin = line.find('var items = [{') + len('var items = [')
                end = line.find('}];') + 1
                item = line[begin:end]
                comments.append(item)
    return comments

list_of_comments = get_all_comments(get_all_blog_posts(my_url))

#just testing to see if it works, change later
for item in list_of_comments:
    if ('name' in item and 'body' in item):
        body_start =item.find('body\': ') + len('body\': \'')
        body_end = item[body_start:].find('\'')
        body = item[body_start:body_start+body_end]
        name_start = item.find('{\'name\': ') + len('{\'name\': \'')
        name_end = item[name_start:].find('\'')
        print item[name_start:name_start+name_end] +':', item[body_start:body_start+body_end]