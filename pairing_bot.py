from __future__ import unicode_literals
import re
import logging


# from https://docs.python.org/2/howto/logging.html#configuring-logging
# set up new logger for this file
logger = logging.getLogger('pairingBot')
logger.setLevel(logging.DEBUG)

# console handler for logging
conLog = logging.StreamHandler()
conLog.setLevel(logging.DEBUG)

# formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# format console logs using formatter
conLog.setFormatter(formatter)

# add console logging transport to logger
logger.addHandler(conLog)


'''
As of now just splits on "," but in the future
it should be able to handle logical operators like
and, or, etc so that user can specify richer queries
'''
def _prepare_args_for_cmd(cmd, str):
    return map(lambda s: '' if s == None else s.strip(), str.split(','))


'''
Cleans up the re.match object
- makes cmd lowercase
- strips trailing whitespaces from args string
'''
def _cleanup_matchobj(match_obj):
    # convert it into dict (cuz python)
    temp = match_obj.groupdict()

    # normalize cmd to lowercase
    temp['cmd'] = temp['cmd'].lower()

    # strip trailing spaces and lower case it all
    temp['args'] = '' if temp['args'] == None else temp['args'].strip().lower()

    return (temp['cmd'], temp['args'])


'''
Handles "add" command
Adds items to the list of things the user is interested in
'''
def _handle_add(db, cmd, args, sender_id, full_name):
    # pull args
    args = _prepare_args_for_cmd(cmd, args)
    db[sender_id] = db.get(sender_id, {})
    db[sender_id]['interests'] = db[sender_id].get('interests', []) + filter(lambda s: False if s == '' else True, args)
    db[sender_id]['full_name'] = full_name
    logger.info('Interests: %r' % db[sender_id])
    return 'Saved ' + ', '.join(args)


'''
Handles "remove" command
Removes items from the things the user is interested in
'''
def _handle_remove(db, cmd, args, sender_id):
    args = _prepare_args_for_cmd(cmd, args)
    db[sender_id] = db.get(sender_id, {})
    old_interests = db[sender_id].get('interests', [])
    db[sender_id]['interests'] = filter(lambda x: False if x in args else True, old_interests)
    logger.info('Interests: %r' % db[sender_id])
    return 'Removed ' + ', '.join(args) + ' from ' + ', '.join(old_interests)


'''
Handle "list" command
Lists the user's current interests
'''
def _handle_list(db, cmd, sender_id):
    interests = db.get(sender_id, {}).get('interests', [])
    return 'You\'re currently interested in pairing on ' + ', '.join(interests)


'''
Handles "search" command
Returns a list of users that are interested in topics passed to search
Future work: Add support for logical operators for richer queries
'''
def handle_search(db, cmd, args, sender_id):
    args = prepare_args_for_cmd(cmd, args)
    db_as_list = [x for x in iter(db.iteritems())]
    list_of_maps_from_db = map(lambda (id, hash): map(lambda i: hash['full_name'] if i.lower() in args else None, hash['interests']), db_as_list)[0]
    deduped = set(list_of_maps_from_db)
    deduped.remove(None)
    return 'The following people are interested in ' + ', '.join(args) + ':\n' + ', '.join(deduped) if len(deduped) != 0 else 'Sorry, I did not find any one who is interested in ' + ', '.join(args) + ' :('


'''
Processes input from the user and performs the action specified
'''
def process_msg(db, content, sender_id, sender_email, full_name):
    logger.info('Input: %r' % content)

    # get some captures
    match_obj = re.match(r'^(?P<cmd>add|remove|search|list)(?P<args>\s+.*)?$', content, re.IGNORECASE)

    if match_obj == None:
        return {
            'content': '`' + content + '` is not a valid command.',
            'sender_email': sender_email
        }

    cmd, args = cleanup_matchobj(match_obj)

    logger.info('Cmd: %r' % cmd)
    logger.info('Args: %r' % args)

    if cmd == 'add':
        return {
            'content': handle_add(db, cmd, args, sender_id, full_name),
            'sender_email': sender_email
        }

    if cmd == 'remove':
        return {
            'content': handle_remove(db, cmd, args, sender_id),
            'sender_email': sender_email
        }

    if cmd == 'list':
        return {
            'content': handle_list(db, cmd, sender_id),
            'sender_email': sender_email
        }

    if cmd == 'search':
        return {
            'content': handle_search(db, cmd, args, sender_id),
            'sender_email': sender_email
        }
