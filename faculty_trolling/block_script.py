import argparse
import requests
from requests_oauthlib import OAuth1
import time
import sys
import os
from email_alert import email_alert
from delete_pid import delete_pid

parser = argparse.ArgumentParser(
    description='Get user specific credentials')
parser.add_argument('-username')
parser.add_argument('-email_address')
parser.add_argument('-access_key', help='twitter access token secret')
parser.add_argument('-access_token', help='twitter access token')
parser.add_argument('-consumer_key', help='twitter consumer key')
parser.add_argument('-consumer_secret', help='twitter consumer secret')
args = parser.parse_args()

auth = OAuth1(args.consumer_key, args.consumer_secret,
              args.access_token, args.access_key)

def generate_block_list():

    params = {'count': 200}
    url = 'https://api.twitter.com/1.1/statuses/mentions_timeline.json'
    response = requests.get(url=url, params=params, auth=auth)

    if response.status_code == 200:
        mentioner_list = []
        for obj in response.json():
            mentioner = obj['user']

            # verified or not
            if mentioner['screen_name'] not in mentioner_list \
                    and not mentioner['verified']:
                mentioner_list.append(mentioner['screen_name'])

        # whether a the faculty follow that person
        block_list = not_friend(mentioner_list)

        return block_list

    else:
        print(response.text)
        delete_pid(os.getpid())
        email_alert(args.email_address, args.username, response.text)
        sys.exit(0)

def not_friend(mentioner_list):
    params = {'screen_name': ','.join(mentioner_list)}
    url = 'https://api.twitter.com/1.1/friendships/lookup.json'
    response = requests.get(url=url, params=params, auth=auth)

    if response.status_code == 200:
        non_friend_list = []
        for person in response.json():
            if 'following' not in person['connections']:
                non_friend_list.append(person['screen_name'])

        return non_friend_list

    else:
        print(response.text)
        delete_pid(os.getpid())
        email_alert(args.email_address, args.username, response.text)
        sys.exit(0)

def generate_blocked_list():
    url = 'https://api.twitter.com/1.1/blocks/list.json'
    response = requests.get(url=url, auth=auth)

    if response.status_code == 200:
        blocked_list = []
        for user in response.json()['users']:
            blocked_list.append(user['screen_name'])

        return blocked_list
    else:
        print(response.text)
        delete_pid(os.getpid())
        email_alert(args.email_address, args.usernamei, response.text)
        sys.exit(0)

def block(mentioner_list):
    for screen_name in mentioner_list:
        params = {'screen_name': screen_name}
        url = 'https://api.twitter.com/1.1/blocks/create.json'
        response = requests.post(url=url, params=params, auth=auth)

        if response.status_code == 200:
            print("blocked screename: ", response.json()['screen_name'])
        else:
            print(response.text)

    return None

def unblock(blocked_list):
    for screen_name in blocked_list:
        params = {'screen_name': screen_name}
        url = 'https://api.twitter.com/1.1/blocks/destroy.json'
        response = requests.post(url=url, params=params, auth=auth)
        if response.status_code == 200:
            print("unblocked screename: ", response.json()['screen_name'])
        else:
            print(response.text)

    return None


if __name__== '__main__':

    tCurrent = time.time()
    count = 0
    while True:

        tIter = time.time()
        count += 1

        if tIter <= tCurrent + 60*60*24*14:
            # stop after 2 weeks

            print('------------perform trolling block------------')
            block_list = generate_block_list()
            print(block_list)
            block(block_list)

            time.sleep(60*5) # 5 minutes
        
        else:
            print("blocker time out!")
            delete_pid(os.getpid())
            email_alert(args.email_address, args.username, "blocker timer out!")
            sys.exit(0)

