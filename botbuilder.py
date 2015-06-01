import zulip
import json
import requests
import random
from pairing_bot import process_msg
import shelve
from logger import logger_setup
import re

logger = logger_setup('botBuilder')

class bot():
    ''' Bot helps people find people to pair with
    '''
    def __init__(self, zulip_username, zulip_api_key, subscribed_streams=[]):
        self.username = zulip_username
        self.api_key = zulip_api_key
        self.subscribed_streams = subscribed_streams
        self.client = zulip.Client(zulip_username, zulip_api_key)
        self.subscriptions = self.subscribe_to_streams()
        self.db = shelve.open('./db', writeback=True)


    ''' Standardizes a list of streams in the form [{'name': stream}]
    '''
    @property
    def streams(self):
        if not self.subscribed_streams:
            streams = [{'name': stream['name']} for stream in self.get_all_zulip_streams()]
            return streams
        else:
            streams = [{'name': stream} for stream in self.subscribed_streams]
            return streams


    def get_all_zulip_streams(self):
        ''' Call Zulip API to get a list of all streams
        '''
        response = requests.get('https://api.zulip.com/v1/streams', auth=(self.username, self.api_key))
        if response.status_code == 200:
            return response.json()['streams']
        elif response.status_code == 401:
            raise RuntimeError('check yo auth')
        else:
            raise RuntimeError(':( we failed to GET streams.\n(%s)' % response)


    def subscribe_to_streams(self):
        ''' Subscribes to zulip streams
        '''
        self.client.add_subscriptions(self.streams)


    def respond(self, msg):
        ''' checks msg against key_word. If key_word is in msg, gets a gif url,
            picks a caption, and calls send_message()
        '''
        if (msg['type'] == 'private' and msg['sender_email'] != zulip_username):
            logger.debug(msg)
            logger.debug('Sender id: %r' % msg['sender_id'])
            # remove bots from the display recipient list and used the 1st non bot user as the person who
            # is trying to save his/her interests
            # T_T
            filtered_display_recipient = filter(lambda hash: False if re.search(r'bot', hash['short_name'], re.IGNORECASE) else True, msg['display_recipient'])
            logger.debug('From: %r', filtered_display_recipient[0]['full_name'])
            reply_msg = process_msg(self.db, msg['content'].strip(), str(msg['sender_id']), msg['sender_email'], filtered_display_recipient[0]['full_name'])
            self.db.sync()
            if reply_msg != None:
                self.send_message(reply_msg)


    def send_message(self, msg):
        ''' Sends a message to zulip stream
        '''
        self.client.send_message({
            'type': 'private',
            'to': msg['sender_email'],
            'content': msg['content']
            })


    def main(self):
        ''' Blocking call that runs forever. Calls self.respond() on every message received.
        '''
        logger.info('Pairing bot started..')
        self.client.call_on_each_message(lambda msg: self.respond(msg))


zulip_username = 'pairingbot-bot@students.hackerschool.com'
zulip_api_key = 'ngUUzHKNDylVYEWNq5Czf8Zqgj1rDAJt'
subscribed_streams = []

new_bot = bot(zulip_username, zulip_api_key, subscribed_streams)
new_bot.main()
