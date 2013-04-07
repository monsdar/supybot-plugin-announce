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
    def __init__(self, channel="", expiration=1, headline="", message="", time=0):
        self.channel = channel
        self.headline = headline
        self.message = message
        self.date = int(time)
        
        #default to a week expiration
        if(expiration == 0):
            expiration = expiration * HOURS
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

    def new(self, irc, msg, args, channel, expiration, message):
        """[<channel>] <expiration> <title>: <message>
        
        Adds an announcement with <title> and <text> to the plugin.
        Expires in <expiration> HOURS.
        If no <channel> is given the current channel will be used. You need to be op in the channel."""
        try:
            (headline, text) = message.split(': ', 1)
        except ValueError:
            irc.reply("Invalid <title> or <message>")
            raise callbacks.ArgumentError
            
        announcement = Announcement(channel, expiration, headline, text, time=time.time())        
        self.announcements.append(announcement)
        irc.replySuccess()
    new = wrap(new, [('checkChannelCapability', 'op'), 'int', 'text'])
    
    def delete(self, irc, msg, args, channel, index):
        """[index]
        
        Removes <index> from the announcements.
        You must have op-rights in your channel to use this."""
        if(len(self.announcements) <= index):
            irc.reply("There is no announcement with index " + str(index))
            return
        
        del self.announcements[index]
        irc.replySuccess()
    delete = wrap(delete, [('checkChannelCapability', 'op'), 'int'])
    
    def listall(self, irc, msg, args):
        """takes no arguments
        
        Lists the announcements by title along with their index."""
        if(len(self.announcements) == 0):
            irc.reply('There are no announcements')
            return
            
        for index, announcement in enumerate(self.announcements):
            irc.reply("<" + str(index) + "> - " + announcement.headline)
    listall = wrap(listall)
    
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
        for announcement in self.announcements:
            if(announcement.channel != channel):
                #announcement is for another channel
                continue
            if( (announcement.date + announcement.expiration) < int(time.time()) ):
                #announcement expired
                continue
            irc.queueMsg( ircmsgs.privmsg(channel, str(announcement)) )
            writtenSomething = True
            
        if not(writtenSomething):
            #do not spam if there is nothing to write about....
            #irc.queueMsg( ircmsgs.privmsg(channel, "No announcements...") )
            pass
    headlines = wrap(headlines, [('checkChannelCapability', 'op')])
    
    def cleanup(self, irc, msg, args, channel):
        """[<channel>]
        
        Cleans up the expired messages for the given <channel>.
        Defaults to the current <channel>. You need to be op in the <channel>."""
        removeIndeces = []
        currentTime = int(time.time())
        for index, announcement in enumerate(self.announcements):
            if not(channel == announcement.channel):
                #not the selected channel
                continue
            if( currentTime <= (announcement.date + announcement.expiration) ):
                #not expired yet
                continue
            removeIndeces.append(index)
        
        for index, announcement in enumerate(removeIndeces):
            del self.announcements[announcement - index]
        
        irc.reply("Removed " + str( len(removeIndeces)) + " announcements")
    cleanup = wrap(cleanup, [('checkChannelCapability', 'op')])
    
Class = Announce


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
