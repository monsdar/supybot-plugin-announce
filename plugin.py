###
# Copyright (c) 2013, Nils Brinkmann
# All rights reserved.
#
#
###

import os
import cPickle
import time

import supybot.callbacks as callbacks
import supybot.conf as conf
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.plugins as plugins
import supybot.utils as utils
from supybot.commands import *

MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY
MONTH = 4 * WEEK

class Announcement():
    def __init__(self, channel="", expiration=WEEK, headline="", message="", time=0):
        self.channel = channel
        self.headline = headline
        self.message = message
        self.date = time
        self.expiration = expiration #int, in seconds
        
    def __str__(self):
        output = ""
        output += "\x02" + self.headline + ":\x02 " + self.message
        return output

class Announce(callbacks.Plugin):
    """Announces headlines to a channel"""
    def __init__(self, irc):
        self.__parent = super(Announce, self)
        self.__parent.__init__(irc)
        
        self.announcements = []

        #read the announcements from file
        filepath = conf.supybot.directories.data.dirize('Announce.db')
        if( os.path.exists(filepath) ):
            try:
                self.announcements = cPickle.load( open( filepath, "rb" ) )
            except EOFError as error:
                irc.reply("Error when trying to load existing data.")
                irc.reply("Message: " + str(error))
        
    def die(self):
        #Pickle the items to a file
        try:
            filepath = conf.supybot.directories.data.dirize('Announce.db')
            cPickle.dump( self.announcements, open( filepath, "wb" ) )
        except cPickle.PicklingError as error:
            print("More: Error when pickling to file...")
            print(error)

    def add(self, irc, msg, args, channel, expiration, message):
        """[<channel>] <expiration> <title>: <message>
        
        Adds an announcement with <title> and <text> to the plugin.
        Expires in <expiration> seconds, default is a week if 0 is given.
        If no <channel> is given the current channel will be used. You need to be op in the channel."""
        try:
            (headline, text) = message.split(': ', 1)
        except ValueError:
            irc.reply("Invalid <title> or <message>")
            raise callbacks.ArgumentError
            
        #TODO: Does not seem to work...
        if(expiration == 0):
            expiration = WEEK
            
        announcement = Announcement(channel, expiration, headline, message, time=time.time())
        self.announcements.append(announcement)
        irc.replySuccess()
    add = wrap(add, [('checkChannelCapability', 'op'), 'int', 'text'])
    #add = wrap(add)
    
    def remove(self, irc, msg, args, channel, index):
        """[index]
        
        Removes <index> from the announcements.
        You must have op-rights in your channel to use this."""
        if(len(self.announcements) <= index):
            irc.reply("There is no announcement with index " + str(index))
            return
        
        del self.announcements[index]
        irc.replySuccess()
    remove = wrap(remove, [('checkChannelCapability', 'op'), 'int'])
    
    def list(self, irc, msg, args):
        """takes no arguments
        
        Lists the announcements by title along with their index."""
        if(len(self.announcements) == 0):
            irc.error('There are no announcements')
            return
            
        for index, announcement in enumerate(self.announcements):
            irc.reply("<" + str(index) + "> - " + announcement.headline)
    list = wrap(list)
    
    def output(self, irc, msg, args, index):
        """<index>
        
        Prints the announcement with the given <index>."""
        if(len(self.announcements) > index):
            announcement = self.announcements[index]
            irc.queueMsg( ircmsgs.privmsg(announcement.channel, str(announcement)) )
        else:
            irc.error("Index " + str(index) + " is not valid")
    output = wrap(output, ['int'])
    
    def headlines(self, irc, msg, args, channel):
        """<channel>
        
        Prints the actual (not expired) headlines of the current given <channel>"""
        writtenSomething = False
        #TODO: This does not print as expected... expired? It works after reload...
        for announcement in self.announcements:
            if(announcement.channel != channel):
                #announcement is for another channel
                continue
            if( (announcement.date + announcement.expiration) > time.time() ):
                #announcement expired
                continue
                
            irc.queueMsg( ircmsgs.privmsg(channel, str(announcement)) )
            writtenSomething = True
            
        if not(writtenSomething):
            irc.queueMsg( ircmsgs.privmsg(channel, "No announcements...") )
            pass
    headlines = wrap(headlines, [('checkChannelCapability', 'op')])
    
Class = Announce


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
