# import os, re, sys, time, datetime
# from os import system
from urllib import urlencode
from cgi import parse_qs, parse_qsl

#twisted
from twisted.python import log
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet import reactor
from twisted.web import  microdom


some_iterator = iter()
next_socket_id = some_iterator

class _ConnectionSocket(LineOnlyReceiver):
    """Transfer data between client server via a socket.
    Inherits from twisited.protocols.basic.LineOnlyReceiver"""

    # ??????
    delimiter=config.NUL

    # arbitrary length
    MAX_LENGTH = 2048
    game = None
    ID = None
    avatar = None
    client_hash = None  # random string used to link the web and socket interfaces.
    
    unlogged_send_modes = ('SUCCESSFUL_OPERATION', 'UPDATE_DATA', 'ERROR')
    unlogged_receive_modes = ('SKIP_TURN', 'BUY_UNIT', 'SELL_UNIT', 'SELL_CUR', 'BUY_CUR', 'BUILD_UNIT')

    def __init__(self):
        """ Constructor"""
        # Set up modes look up
        

        # dictonaries_module, if needed
        # 
        #

        pass



    def connectionMade(self):
        """Add self.transport to stage's list"""
        self.ID = next_socket_id()
        self.player = self.factory.players #reset sometime later
        self.send('SET', ID=self.ID)
        # so client knows who it is

    
    def client_setup(self):
        """On connection, or on reset, sends the client data about other users,
         market exchanges and so on"""

            players = game.get_players_list()
            market = game.get_market_exchange_list()
            chat_history = game.get_chat_history_list()

            #send the total counts of things to load.
            self.send('GAME_DETAILS',
                      players = len(players),
                      market = len(market),
                      chat_history = len(chat_history),
                      msg = self.game.details_message)

            # send the users, market_data and chat_history
            for pl in players:
                self.send('LOAD_PLAYERS',
                          ID = pl.ID,
                          name = pl.name,
                          country = pl.country,
                          fund = pl.fund,
                          vvp = pl.vvp,
                          curs = pl.curs
                          # ?           
                          )

            for ex in market:
                self.send("LOAD_MARKET",
                          ID = ex.ID,
                          seller_id = ex.seller_id,
                          seller_name = ex.seller_name,
                          cur_id   = ex.cur_id,
                          val = ex.val
                          # ?  
                          )
                
                
            for msg in chat_history: 
                self.send("LOAD_CHAT",
                          ID = x.ID,
                          name = x.name,
                          time = x.time, 
                          msg = x.msg
                          )


    # Disconnecting from the stage (pushing back button, closing browser, entering new url)
    def connectionLost(self, reason='no known reason'):
        """
        blah-blah-blah
        if session.connected:
            session.break()
            """

        p = self.factory.clients.pop(self.client_hash, self.factory.players)


    def send(self, mode, **kwargs):
        kwargs['mode'] = mode
        msg = urlencode(kwargs)
        try:
            self.transport.write(msg + config.NUL)
            if config.VERBOSE or mode not in self.unlogged_send_modes:
                log.msg('SENT: ' + msg)
        except:
            log.msg("Unexpected error: %s : %s" %(sys.exc_info()[0], sys.exc_value)) 



    def lineLengthExceeded(self, line):
        log.msg('The maximum length of data was exceeded. Current length limit is %s' %self.MAX_LENGTH)
    
    
    def lineReceived(self, data):

        try:
            d = dict( parse_qsl(data, 1, 1) )
            mode = d.pop('mode')
        except (ValueError, KeyError):
            mode = None

        handler = self.modes.get(mode, self.unknown_mode)
        try:
            handler(**d)
        except Exception, e:
            print "ERROR handling socket line: '%s'" % data
            print "called %s with args %s" %(handler, d)
            print "got exception %s" % e
            #send an error message to the client?

    def unknown_mode(self, **kwargs):
        """When you don't know what to do, do nothing"""
        log.msg('unknown mode in socket: available modes are: %s' % (self.modes.keys(),))

    def error(self, msg):
        """Send an error message to the client"""
        self.send('ERR', error=msg)



    
class SocketFactory(Factory):
    """Produces _ConnectionSocket instances"""
    def __init__(self, data):
        self.users = data.users
        self.clients = data.clients
        self.players = data.users.players

    protocol = _UpstageSocket
        
