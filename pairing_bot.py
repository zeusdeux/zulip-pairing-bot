from __future__ import unicode_literals
import re
from logger import logger_setup


logger = logger_setup('pairingBot')

def _prepare_args_for_cmd(cmd, str):
    """As of now just splits on "," but in the future it should be able to
    handle logical operators like and, or, etc so that user can specify richer
    queries.
    """

    return map(lambda s: '' if s == None else s.strip(), str.split(','))


def _cleanup_matchobj(match_obj):
    """Cleans up the re.match object:
      - makes cmd lowercase
      - strips trailing whitespaces from args string
    """

    # convert it into dict (cuz python)
    temp = match_obj.groupdict()

    # normalize cmd to lowercase
    temp['cmd'] = temp['cmd'].lower()

    # strip trailing spaces and lower case it all
    temp['args'] = '' if temp['args'] == None else temp['args'].strip().lower()

    return (temp['cmd'], temp['args'])


def _handle_add(db, cmd, args, sender_id, full_name):
    """Handles "add" command.

    Adds items to the list of things the user is interested in.
    """

    # pull args
    args = _prepare_args_for_cmd(cmd, args)
    db[sender_id] = db.get(sender_id, {})
    db[sender_id]['interests'] = list(set(db[sender_id].get('interests', []) + filter(lambda s: False if s == '' else True, args)))
    db[sender_id]['full_name'] = full_name
    logger.info('Interests: %r' % db[sender_id])
    return 'Saved ' + ', '.join(args)


def _handle_remove(db, cmd, args, sender_id):
    """Handles "remove" command.

    Removes items from the things the user is interested in.
    """

    args = _prepare_args_for_cmd(cmd, args)
    db[sender_id] = db.get(sender_id, {})
    old_interests = db[sender_id].get('interests', [])
    db[sender_id]['interests'] = filter(lambda x: False if x in args else True, old_interests)
    logger.info('Interests: %r' % db[sender_id])
    return 'Removed ' + ', '.join(args) + ' from ' + ', '.join(old_interests)


def _handle_list(db, cmd, sender_id):
    """Handle "list" command.

    Lists the user's current interests.
    """

    interests = db.get(sender_id, {}).get('interests', [])
    return 'You\'re currently interested in pairing on: \n\n* ' + '\n * '.join(interests)


def _handle_search(db, cmd, args, sender_id):
    """Handles "search" command.

    Returns a list of users that are interested in topics passed to search.
    Future work: Add support for logical operators for richer queries.
    """

    args = _prepare_args_for_cmd(cmd, args)
    db_as_list = [x for x in iter(db.iteritems())]
    hashes = map(lambda (id, hash): hash, db_as_list)
    result = filter(lambda hash: True if len(filter(lambda i: True if re.search(re.escape(r'%s' % i), ', '.join(hash['interests']), re.IGNORECASE) != None else False, args)) > 0 else False, hashes)

    result_str = '\n'.join(map(lambda hash: '* ' + hash['full_name'] + ' is interested in '+ ', '.join(filter(lambda r: False if r == '' else True, map(lambda arg: ', '.join(filter(lambda i: True if re.search(re.escape(r'%s' % arg), i) != None else False, hash['interests'])), args))), result))

    return 'The following people are interested in ' + ', '.join(args) + ':\n\n' + result_str if len(result) != 0 else 'Sorry, I did not find any one who is interested in ' + ', '.join(args) + ' :('


def _handle_help():
    """Provides the help string."""

    help_txt = ''
    help_txt += 'To use Pairing Bot, send it a PM using the commands below:\n\n'
    help_txt += 'Command | Description \n'
    help_txt += ':--- | :--- \n'
    help_txt += '`add or a <comma separated args>` | Adds the arguments to your list of interests. Example `add haskell` or `add clojure, js` \n'
    help_txt += '`remove or r<comma separated args>` | Removes the arguments from your list of interest if they exist in it. Example `remove js` or `remove js, erlang` \n'
    help_txt += '`search or s<comma separated args>` | Returns a list of people who have specified one or more of the arguments in their list of interests. Example `search js, python` \n'
    help_txt += '`list or l or ls` | Lists your currently saved interests \n'
    help_txt += '`help or h` | Shows this table \n\n\n'
    help_txt += 'Made with :heart_decoration: at Recurse Center\n'

    return help_txt


def _build_response(sender_email, content):
    """Build the reply object that is consumed by the method that called process_msg.
    """

    return {
        'content': content,
        'sender_email': sender_email
    }


def process_msg(db, content, sender_id, sender_email, full_name):
    """Processes input from the user and performs the action specified."""

    logger.info('Input: %r' % content)

    # get some captures
    match_obj = re.match(r'^(?P<cmd>add|remove|search|list|help|a|r|rm|s|l|ls|h)(?P<args>\s+.*)?$', content, re.IGNORECASE)

    if match_obj == None:
        return {
            'content': '`' + content + '` is not a valid command.',
            'sender_email': sender_email
        }

    cmd, args = _cleanup_matchobj(match_obj)

    logger.info('Cmd: %r' % cmd)
    logger.info('Args: %r' % args)

    if cmd == 'add' or cmd == 'a':
        return _build_response(sender_email, _handle_add(db, cmd, args, sender_id, full_name))

    if cmd == 'remove' or cmd == 'r' or cmd == 'rm':
        return _build_response(sender_email, _handle_remove(db, cmd, args, sender_id))

    if cmd == 'list' or cmd == 'l' or cmd == 'ls':
        return _build_response(sender_email, _handle_list(db, cmd, sender_id))

    if cmd == 'search' or cmd == 's':
        return _build_response(sender_email, _handle_search(db, cmd, args, sender_id))

    if cmd == 'help' or cmd == 'h':
        return _build_response(sender_email, _handle_help())
