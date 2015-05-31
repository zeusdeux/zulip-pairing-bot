# zulip-pairing-bot
A zulip bot that helps people find others to pair with.

For my first project in Python, I wanted to work on something simple yet fun.

Zulip bots are both of those, so with the help of @kokeshii, I wrote this pairing bot.

Pairing bot gives the user a few commands that let 'em add/remove topics they are interested in
and to search for users based on topic they supply.

## Commands
PM pairing bot with messages that use the commands listed below:

Command | Description
--- | ---
`add <comma separated args>` | Adds the arguments to your list of interests. Example `add haskell` or `add clojure, js`
`remove <comma separated args>` | Removes the arguments from your list of interest if they exist in it. Example `remove js` or `remove js, erlang`
`search <comma separated args>` | Returns a list of people who have specified one or more of the arguments in their list of interests. Example `search js, python`
list | Lists your currently saved interests. Example `list`
help | Shows this table. Example `help`

PS: Zulip doesn't seem to let me format my help text as a table. If you want to fix it, [here's the issue](https://github.com/zeusdeux/zulip-pairing-bot/issues/1).

Made with :heart_decoration: at Recurse Center

> Icon is people by NATAPON CHANTABUTR from the Noun Project.
