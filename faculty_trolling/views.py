from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
import subprocess
from .models import Proccess
from .models import Twitter
import os
import signal
import oauth2
import urllib.parse
from django.contrib import messages
import json

with open('/home/ubuntu/faculty_trolling/faculty_trolling/config.json','r') as f:
    cred = json.load(f)
    consumer_key = cred['consumer_key']
    consumer_secret = cred['consumer_secret']

request_token_url = 'https://api.twitter.com/oauth/request_token'
access_token_url = 'https://api.twitter.com/oauth/access_token'
authorize_url = 'https://twitter.com/oauth/authorize'
consumer = oauth2.Consumer(consumer_key, consumer_secret)

def get_tokens(user_id):

    client = oauth2.Client(consumer)
    resp, content = client.request(request_token_url, "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response %s." % resp['status'])

    request_token = dict(urllib.parse.parse_qsl(content.decode("utf-8")))

    # if this user already has a temp tokens, update
    # if not, create a new record
    if not Twitter.objects.filter(user_id=user_id).exists():
        Twitter.objects.create(user_id=user_id,
                           oauth_token=request_token['oauth_token'],
                           oauth_token_secret=request_token['oauth_token_secret']
                           )
    else:
        Twitter.objects.filter(user_id=user_id).update(
            oauth_token= request_token['oauth_token'],
            oauth_token_secret=request_token['oauth_token_secret'])

    return authorize_url + '?oauth_token=' +request_token['oauth_token']


def auth(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            redirect_url = get_tokens(request.user.id)

            return HttpResponseRedirect(redirect_url)
    else:
        return HttpResponseRedirect('/account/login')

def auth_callback(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            oauth_verifier = request.GET['oauth_verifier']

            # retrieve oauth token and secret from twitter table
            oauth_token = Twitter.objects.filter(
                user_id = request.user.id).values('oauth_token')[0]['oauth_token']
            oauth_token_secret = Twitter.objects.filter(
                user_id = request.user.id).values('oauth_token_secret')[0]['oauth_token_secret']

            token = oauth2.Token(oauth_token, oauth_token_secret)
            token.set_verifier(oauth_verifier)

            client = oauth2.Client(consumer, token)
            resp, content = client.request(access_token_url, 'POST')
            credentials = dict(urllib.parse.parse_qsl(content.decode("utf-8")))

            access_token = credentials['oauth_token']
            access_key = credentials['oauth_token_secret']

            # save access token and secret to twitter table
            Twitter.objects.filter(user_id=request.user.id).update(
                access_token=access_token,
                access_key=access_key)
        messages.success(request, 'You have succesfully granted us access '
                                  'to perform blocking on your behalf.')
        return HttpResponseRedirect('/block')
    else:
        return HttpResponseRedirect('/account/login')

def block(request):
    if request.user.is_authenticated:

        template = loader.get_template('./index.html')
        context = {
            'title': 'faculty trolling',
            'user_name': request.user.username
        }

        if request.method == 'GET':
            return HttpResponse(template.render(context, request))

        elif request.method == 'POST':
            # get access token and access key for that user
            user_id = request.user.id

            # check if user has access token and access secret
            # saved in Twitter table
            if Twitter.objects.filter(user_id=user_id).exists():
                access_token = Twitter.objects.filter(
                    user_id=user_id).values('access_token')[0]['access_token']
                access_key = Twitter.objects.filter(
                    user_id=user_id).values('access_key')[0]['access_key']

                # check if twitter table is complete
                if access_token == '' or access_key == '':
                    messages.error(request, 'Something wrong went wrong our internal ' \
                                         'record of your Twitter account ' \
                                         'credentials. Please re-authorize again!')


                else:
                    # check if user already has a troll blocker running
                    if Proccess.objects.filter(user_id=user_id).exists():
                        messages.error(request, 'You have already launched ' \
                                             'Troller Blocker. If you wish ' \
                                             'to stop blocking, please press ' \
                                             'STOP button.')
                    else:
                        # subprocess command
                        script = '/home/ubuntu/faculty_trolling/' \
                                 'faculty_trolling/block_script.py'
                        command = ['python3', script, '-consumer_key', consumer_key,
                                   '-consumer_secret', consumer_secret,
                                   '-access_token', access_token,
                                    '-access_key', access_key,
                                   '-username', request.user.username,
                                   '-email_address', request.user.email]
                        proc = subprocess.Popen(command)

                        # save user id and pid to the database
                        Proccess.objects.create(user_id=user_id, pid =proc.pid)
                        messages.success(request, 'Troller Blocker succesfully launched!')

            else:
                messages.error(request, 'You have to authorize Troll Blocker '
                                        'with your Twitter account.')
            return HttpResponseRedirect('/block')

    else:
        messages.error(request, 'You have not log in yet!')
        return HttpResponseRedirect('/account/login')

def stop(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            # get pid from username
            user_id = request.user.id

            # find pid corresponding to that username, kill the process
            if Proccess.objects.filter(user_id=user_id).exists():
                for pid in Proccess.objects.filter(user_id=user_id).values("pid"):
                    try:
                        os.kill(int(pid['pid']), signal.SIGINT)
                        print('kill pid:', pid['pid'])
                    except ProcessLookupError as e:
                        print(e)

                # delete that entry in the Proccess database
                Proccess.objects.filter(user_id=user_id).delete()

                messages.error(request, 'Your Troll Blocker is stopped!')

            else:
                messages.error(request,
                               'Your Troll Blocker has already been stopped!')

            # unblock script
            return HttpResponseRedirect('/block')
    else:
        return HttpResponseRedirect('/account/login')
