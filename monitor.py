#!/usr/bin/python

from RPi import GPIO
from time import sleep, time
from datetime import datetime

import pickle
import tornado.ioloop
import tornado.web

import signal
import sys
import subprocess

import logging
import logging.handlers

def date_back( theDateAndTime, precise = False, fromDate = None ):
    # provides a human readable format for a time delta
    #   @param theDateAndTime this is time equal or older than now or the date in 'fromDate'
    #   @param precise        when true then milliseconds and microseconds are included
    #   @param fromDate       when None the 'now' is used otherwise a concrete date is expected
    #   @return the time delta as text
    #
    # @note I don't calculate months and years because those vary (28,29,30 or 31 days a month
    # and 365 or 366 days the year depending on leap years). In addition please refer
    # to the documentation for timedelta limitations.
    if not fromDate:
        fromDate = datetime.now( )
    if not theDateAndTime:
        theDateAndTime = fromDate
    if theDateAndTime == fromDate:
        return "Now"
    elif theDateAndTime > fromDate:
        return None

    delta = fromDate - theDateAndTime

    # the timedelta structure does not have all units; bigger units are converted
    # into given smaller ones (hours -> seconds, minutes -> seconds, weeks > days, ...)
    # but we need all units:
    deltaMinutes      = delta.seconds // 60
    deltaHours        = delta.seconds // 3600
    deltaMinutes     -= deltaHours * 60
    deltaWeeks        = delta.days    // 7
    deltaSeconds      = delta.seconds - deltaMinutes * 60 - deltaHours * 3600
    deltaDays         = delta.days    - deltaWeeks * 7
    deltaMilliSeconds = delta.microseconds // 1000
    deltaMicroSeconds = delta.microseconds - deltaMilliSeconds * 1000

    valuesAndNames =[ ( deltaWeeks  ,"week"   ), ( deltaDays   , "day"    ),
                      ( deltaHours  ,"hour"   ), ( deltaMinutes, "minute" ),
                      ( deltaSeconds,"second" ) ]
    if precise:
        valuesAndNames.append( ( deltaMilliSeconds, "millisecond" ) )
        valuesAndNames.append( ( deltaMicroSeconds, "microsecond" ) )

    text = ""
    for value, name in valuesAndNames:
        if value > 0:
            text += len(text)   and ", " or ""
            text += "%d %s" % (value, name)
            text += (value > 1) and "s" or ""

    # replacing last occurrence of a comma by an 'and'
    if text.find(",") > 0:
        text = " and ".join(text.rsplit(", ",1))

    return text + " ago" if len(text) > 0 else text

class Sensor:
    door_states = {
        GPIO.HIGH: 'open',
        GPIO.LOW: 'closed'
    }
    zone_states = {
        GPIO.HIGH: 'active',
        GPIO.LOW: 'quiet'
    }
    next_index = 0
    managed_list = [ ]
    state_fname = "/home/pi/monitor.pickle"
    GPIO.setmode( GPIO.BOARD )

    def __init__( self, gpio, label, state, pull_up_down, state_names ):
        self.gpio = gpio
        self.label = label
        self.state = state
        self.pull_up_down = pull_up_down
        self.state_names = state_names
        self.timestamp = datetime.now( )
        self.gpio_setup( )

    def gpio_setup( self ):
        GPIO.setup( self.gpio, GPIO.IN, pull_up_down = self.pull_up_down )

    def __str__( self ):
        return ( "{} is {}".format( self.label, self.state_names[ self.state ] ) )

    def poll( self ):
        current_state = GPIO.input( self.gpio )
        if self.state != current_state:
            self.state = current_state
            if current_state == GPIO.HIGH:
                self.timestamp = datetime.now( )
                logger.critical( self )
            else:
                logger.info( self )

    @staticmethod
    def poll_next_in_list( ):
        Sensor.managed_list[ Sensor.next_index ].poll( )
        logger.debug( Sensor.managed_list[ Sensor.next_index ] )
        Sensor.next_index = ( Sensor.next_index + 1 ) % len( Sensor.managed_list )

    @staticmethod
    def all_gpio_setup( ):
        for sensor in Sensor.managed_list:
            sensor.gpio_setup( )

    @staticmethod
    def configure_probes( ):
        Sensor.next_index = 0
        try:
            Sensor.managed_list = Sensor.load_state( )
            Sensor.all_gpio_setup( )
        except:
            Sensor.managed_list = [
                Sensor( 8, 'Car Bay Door', GPIO.LOW, GPIO.PUD_UP, Sensor.door_states ),
                Sensor( 10, 'Equipment Bay Door', GPIO.LOW, GPIO.PUD_UP, Sensor.door_states ),
                # Sensor( 12, 'Side Door', GPIO.LOW, GPIO.PUD_UP, Sensor.door_states ),
                Sensor( 16, 'Equipment Bay', GPIO.LOW, GPIO.PUD_UP, Sensor.zone_states ),
                # Sensor( 18, 'Car Bay', GPIO.LOW, GPIO.PUD_UP, Sensor.zone_states )
            ]

    @staticmethod
    def save_state( ):
        with open( Sensor.state_fname, "w" ) as json_file:
            pickle.dump( Sensor.managed_list, json_file )

    @staticmethod
    def load_state( ):
        with open( Sensor.state_fname, "r" ) as json_file:
            return pickle.load( json_file )

class MainHandler( tornado.web.RequestHandler ):
    @staticmethod
    def service_status( ):
        return subprocess.check_output( [ 'systemctl', 'status', 'monitor' ] )

    @staticmethod
    def make_app( ):
        return tornado.web.Application( [ ( r"/", MainHandler ), ] )

    def get( self ):
        self.write( "<head>" )
        self.write( "<title>Sensors</title>" )
        self.write( "<meta http-equiv=\"refresh\" content=\"5\" />" )
        self.write( "</head>" )
        self.write( "<table style=\"font-family: Verdana, Geneva, sans-serif\" border=\"1\">" )
        self.write( "<thead><tr style=\"background: #6699ff\">" )
        self.write( "<td>Opened or Active Timestamp</td>" )
        self.write( "<td>State</td>" )
        self.write( "<td>Last Opened or Active</td>" )
        self.write( "</tr></thead>" )
        self.write( "<tbody>" )
        for sensor in Sensor.managed_list:
            style = "background: red" if sensor.state == GPIO.HIGH else "background: white"
            self.write( "<tr style=\"{}\">".format( style ) )
            self.write( "<td>{}</td>".format( sensor.timestamp.strftime( "%a %b %d %I:%M:%S %p" ) ) )
            self.write( "<td>{}</td>".format( sensor ) )
            self.write( "<td>{}</td>".format( date_back( sensor.timestamp ) ) )
            self.write( "</tr>" )
        self.write( "</tbody>" )
        self.write( "</table>" )
        self.write( "<br>" )
        self.write( self.service_status( ).replace( "\n", "<br>" ) )

def signal_handler( sig, frame ):
    logger.critical( " graceful exit ... " )
    Sensor.save_state( )
    GPIO.cleanup( )
    sys.exit( 0 )

try:
    logger = logging.getLogger( 'Security Monitor' )
    logger.setLevel( logging.INFO )
    handler = logging.handlers.SysLogHandler( address = ( '192.168.2.16', 514 ), facility = logging.handlers.SysLogHandler.LOG_DAEMON )
    handler.setLevel( logging.INFO )
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter( formatter )
    logger.addHandler( handler )

    signal.signal( signal.SIGTERM, signal_handler )

    Sensor.configure_probes( )
    if __name__ == "__main__":
        app = MainHandler.make_app( )
        app.listen( 8888 )
        tornado.ioloop.PeriodicCallback( Sensor.poll_next_in_list, 100 ).start( )
        tornado.ioloop.PeriodicCallback( Sensor.save_state, 900000 ).start( )
        tornado.ioloop.IOLoop.current( ).start( )
finally:
    GPIO.cleanup( )

exit( 0 )
