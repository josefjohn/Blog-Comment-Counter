'''
Created on Apr 1, 2013

@author: JosefJohn, Gautam Jain
'''
from comment_counter import * #
from rfc3339 import * #

start_of_week = [1359417600, 1360022400, 1360627200, 1361232000, 1361836800,
                 1362441600, 1363046400, 1363651200, 1364256000, 1364860800,
                 1365465600, 1366070400, 1366675200, 1367280000, 1367884800,
                 1368489600, 1369174400]

blog_url_to_blog_id = {}
blog_id_to_author_id = {}

#returns list of dictionaries
#each dictionary maps to a week
#each dictionary contains author_id keys mapping to a set of comment_ids for that week
#for each dictionary, keys are author_id, values are sets of the comments
#call len(dict[author_id]) to get comments for a given week
def get_total_comments():
    total_comments_dictionary_for_week = []
    for i in range(0,start_of_week.__len__()-1):
        total_comments_dictionary_for_week.append(dict())
    for blog_id in blog_id_to_author_id.iterkeys(): #
        posts = get_posts(blog_id)
        for post in posts:
            list_of_comments_dict = get_comments(blog_id, post)
            for comment_dict in list_of_comments_dict:
                author_id = comment_dict['author_id']
                comment_id = comment_dict['comment_id']
                publish_date = comment_dict['publish_date']
                week = get_week_from_publish_date(publish_date)
                if week < 0 or week > 16:
                    print "error"
                    return #change this
                week_comments_dict = total_comments_dictionary_for_week[week]
                if author_id in week_comments_dict.keys():
                    week_comments_dict[author_id] = week_comments_dict[author_id].add(comment_id)
                else:
                    set_of_comment_ids = set() # set wiht comment_ids
                    set_of_comment_ids.add(comment_id)
                    week_comments_dict[author_id] = set_of_comment_ids
    return total_comments_dictionary_for_week
          
def get_week_from_publish_date(publish_date):
    date_in_long = strtotimestamp(publish_date)
    for i in range(0,start_of_week.__len__()-1):
        if date_in_long > start_of_week[i] and date_in_long < start_of_week[i+1]:
            print "week ", i
            return i
    return -1
          
def get_blog_id():
    dict = {}
    response = blogger.blogs().getByUrl(
        url='http://gautam190g.blogspot.com',
        fields="id").execute()
    dict[response['id']] = 1
    return dict

blog_id_to_author_id = get_blog_id()
get_total_comments()