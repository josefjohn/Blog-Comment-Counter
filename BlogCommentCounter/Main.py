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
                                
print get_all_blog_posts(my_url)