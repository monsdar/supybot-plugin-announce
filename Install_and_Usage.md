# Installation and Usage #

## Prerequisites ##
This plugin has been tested with Python 2.7.3.

I'm using supybot 0.83.4.1. As there are no information about the downward compatibility of supybot I recommend using at least this version.

## Install ##
Simply put the Sourcecode into a directory called `Announce` into your supybot plugin directory.
You can load the plugin by performing the command
```
load Announce
```
in your IRC client.

## Usage ##
You can use supybots builtin help system to get detailed information about the plugin. The following is an example of how to use the plugin. Note that my nickname here is 'monsdar' while the Bot is called 'Android':

```
#load the plugin
<monsdar> @load Announce

#add 2 announcements with 24h and 36h expiration time
<monsdar> @announce add 24 Example Title #1: This is announcement #1
<monsdar> @announce add 36 Example Title #2: This is announcement #2

#display the current headlines
<monsdar> @headlines
<@Android> Example Title #1: This is announcement #1
<@Android> Example Title #2: This is announcement #2

#list all the headlines
<monsdar> @announce list
<@Android> monsdar: <0> - Example Title #1
<@Android> monsdar: <1> - Example Title #2

#...30 hours later, item #1 is expired...
#let's clean up a bit
<monsdar> @announce cleanup
<@Android> monsdar: Removed 1 announcements
```

Now let's see how we could create a regular output via the Supybot plugin scheduler:

```
#load the plugins
<monsdar> @load Scheduler
<monsdar> @load Announce

#add some announcements
<monsdar> @announce add 24 Example Title #1: This is announcement #1
<monsdar> @announce add 36 Example Title #2: This is announcement #2

#add them to a repeat-schedule
<monsdar> @scheduler repeat myHeadlines 20 headlines

#...20 seconds later...
<@Android> Example Title #1: This is announcement #1
<@Android> Example Title #2: This is announcement #2
#...and so on...

#let's add a regular cleanup
#so our DB does not get cluttered with old news
<monsdar> @scheduler repeat myHeadlines 300 announce cleanup
```