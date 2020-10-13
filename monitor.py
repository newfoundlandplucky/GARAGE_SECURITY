#!/usr/bin/python3
#
# https://github.com/friendlyarm/RPi.GPIO_NP
#
# This is a modified version RPi.GPIO for NanoPi Duo/Duo2. We call it RPi.GPIO_NP.
# It is based on the original RPi.GPIO. The RPi.GPIO_NP API usage are the same to
# the original RPi.GPIO.
#
from RPi import GPIO
from time import sleep, time
from datetime import datetime

import os
import sys
import subprocess
import signal

import tornado.ioloop
import tornado.web
import pickle

import smbus2
import bme280

import logging
import logging.handlers

class Sensor:
    class pin:
        PA11 = 8
        PA12 = 10
        PA13 = 12
        PA14 = 14
        PA16 = 16
        PA15 = 18
        PG7 = 20
        PG6 = 22
        PG11 = 11

    class activity:
        INVERT = True
        PASSTHRU = False

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
    state_path = os.path.join( os.path.sep, 'var', 'lib', 'monitor' )
    state_filename = "savestate.pickle"
    state_fullname = os.path.join( state_path, state_filename )
    state_extension = "."

    i2c_port = 0
    i2c_address = 0x77
    i2c_bus = smbus2.SMBus( i2c_port )
    bme280_calibration = bme280.load_calibration_params( i2c_bus, i2c_address )

    GPIO.setmode( GPIO.BOARD )

    def __init__( self, order, gpio, label, invert, state_names ):
        self.order = order
        self.gpio = gpio
        self.label = label
        self.state = None
        self.invert = invert
        self.pull_up_down = GPIO.PUD_UP
        self.state_names = state_names
        self.timestamp = None
        self.gpio_setup( )

    def normalized_state( self ):
        return GPIO.HIGH if self.state == GPIO.HIGH and self.invert == False or \
                            self.state == GPIO.LOW and self.invert == True else GPIO.LOW

    def is_active( self ):
        return self.normalized_state( ) == GPIO.HIGH

    def state_name( self ):
        return self.state_names[ self.normalized_state( ) ]

    def __str__( self ):
        return "{} is {}".format( self.label, self.state_name( ) )

    def gpio_setup( self ):
        GPIO.setup( self.gpio, GPIO.IN, pull_up_down = self.pull_up_down )

    def poll( self ):
        current_state = GPIO.input( self.gpio )
        if self.state != current_state:
            self.state = current_state
            if self.normalized_state( ) == GPIO.HIGH:
                self.timestamp = datetime.now( )
                logger.critical( self )
            else:
                logger.info( self )

    def date_back( self ):
        time_now = datetime.now( )
        if self.timestamp is None:
            return "Unknown"
        if self.timestamp == time_now:
            return "Now"
        elif self.timestamp > time_now:
            self.timestamp = None
            return "Unknown"

        delta = time_now - self.timestamp

        deltaMinutes      = delta.seconds // 60
        deltaHours        = delta.seconds // 3600
        deltaMinutes     -= deltaHours * 60
        deltaWeeks        = delta.days // 7
        deltaSeconds      = delta.seconds - deltaMinutes * 60 - deltaHours * 3600
        deltaDays         = delta.days - deltaWeeks * 7

        valuesAndNames = [ ( deltaWeeks, "week" ), ( deltaDays,    "day"    ),
                           ( deltaHours, "hour" ), ( deltaMinutes, "minute" ) ]

        text = ""
        for value, name in valuesAndNames:
            if value > 0:
                text += len( text ) and ", " or ""
                text += "%d %s" % ( value, name )
                text += ( value > 1 ) and "s" or ""
        if text.find( "," ) > 0:
            text = " and ".join( text.rsplit( ", ", 1 ) )
        if len( text ) is 0:
            text = "<1 minute"

        return text + " ago" if len( text ) > 0 else text

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
    def default_list( ):
        return [
            Sensor( 1, Sensor.pin.PG7,  'Car Bay Door',       Sensor.activity.PASSTHRU, Sensor.door_states ),
            Sensor( 2, Sensor.pin.PA15, 'Car Bay',            Sensor.activity.PASSTHRU, Sensor.zone_states ),
            Sensor( 3, Sensor.pin.PA14, 'Driveway Lamp',      Sensor.activity.INVERT,   Sensor.zone_states ),
            Sensor( 4, Sensor.pin.PG6,  'Equipment Bay Door', Sensor.activity.PASSTHRU, Sensor.door_states ),
            Sensor( 5, Sensor.pin.PA16, 'Equipment Bay',      Sensor.activity.PASSTHRU, Sensor.zone_states ),
            Sensor( 6, Sensor.pin.PA13, 'Side Door',          Sensor.activity.PASSTHRU, Sensor.door_states ),
            Sensor( 7, Sensor.pin.PG11, 'Side Door Lamp',     Sensor.activity.INVERT,   Sensor.zone_states ),
        ]

    @staticmethod
    def add_or_update( target ):
        for sensor in Sensor.managed_list:
            if sensor.label == target.label:
                sensor.order = target.order
                sensor.gpio = target.gpio
                return sensor
        Sensor.managed_list.append( target )
        return target

    @staticmethod
    def configure_probes( ):
        Sensor.next_index = 0
        try:
            Sensor.managed_list = Sensor.load_state( )
            for sensor in Sensor.default_list( ):
                Sensor.add_or_update( sensor )
        except:
            Sensor.managed_list = Sensor.default_list( )
        Sensor.all_gpio_setup( )

    @staticmethod
    def backup_fullname( ):
        from stat import S_ISREG, ST_MTIME, ST_MODE
        ARRAY_OLDEST = 0
        TUPLE_FILENAME = 1

        path = Sensor.state_path
        target = Sensor.state_filename + Sensor.state_extension
        filenames = [ os.path.join( path, filename ) for filename in os.listdir( path ) if target in filename ]
        if len( filenames ) < 10:
            return Sensor.state_fullname + Sensor.state_extension + str( len( filenames ) )
        filestats = [ ( os.stat( filename ), filename ) for filename in filenames ]
        filedates = sorted( [ ( filestate[ST_MTIME], filename ) for filestate, filename in filestats ] )

        return filedates[ARRAY_OLDEST][TUPLE_FILENAME]

    @staticmethod
    def save_state( ):
        os.rename( Sensor.state_fullname, Sensor.backup_fullname( ) )
        with open( Sensor.state_fullname, 'wb' ) as json_file:
            pickle.dump( Sensor.managed_list, json_file )

    @staticmethod
    def load_state( ):
        logger.critical( "Reading state from " + Sensor.state_fullname )
        with open( Sensor.state_fullname, 'rb' ) as json_file:
            return pickle.load( json_file )

    @staticmethod
    def bme280_sample( ):
        return bme280.sample( Sensor.i2c_bus, Sensor.i2c_address, Sensor.bme280_calibration )

class MainHandler( tornado.web.RequestHandler ):
    @staticmethod
    def service_status( ):
        try:
            return subprocess.check_output( [ 'systemctl', 'status', 'monitor' ] )
        except:
            return "Not running as a service."

    @staticmethod
    def make_app( ):
        handlers = [
            ( r'/(favicon\.ico)', tornado.web.StaticFileHandler, { "path" : "/var/lib/monitor" } ),
            ( r'/(banner\.png)', tornado.web.StaticFileHandler, { "path" : "/var/lib/monitor" } ),
            ( r'^/$', MainHandler ),
        ]
        return tornado.web.Application( handlers )

    def get( self ):
        self.write( "<head>" )
        self.write( "<title>Sensors</title>" )
        self.write( "<meta http-equiv=\"refresh\" content=\"15\" />" )
        self.write( "<link rel=\"Shortcut Icon\" href=\"/favicon.ico\" />" )
        self.write( "</head>" )
 
        self.write( "<table style=\"font-family: Verdana, Geneva, sans-serif\" border=\"1\">" )
        self.write( "<thead>" )

        bme280_data = Sensor.bme280_sample( )
        self.write( "<tr background=\"/banner.png\">" )
        self.write( "<td colspan=\"3\" style=\"color: white\">" )
        self.write( "Time: {0:%A %B %d, %I:%M:%S %p}</br>".format( bme280_data.timestamp ) )
        self.write( "Temperature: {0:0.0f} °C</br>".format( bme280_data.temperature ) )
        self.write( "Pressure: {0:0.0f} hPa</br>".format( bme280_data.pressure ) )
        self.write( "Humidity: {0:0.0f} % rH".format( bme280_data.humidity ) )
        self.write( "</td>" )
        self.write( "</tr>" )

        self.write( "<tr style=\"background: #6699ff\">" )
        self.write( "<td>Opened or Active Timestamp</td>" )
        self.write( "<td>State</td>" )
        self.write( "<td>Last Opened or Active</td>" )
        self.write( "</tr>" )
        self.write( "</thead>" )

        self.write( "<tbody>" )
        for sensor in sorted( Sensor.managed_list, key = lambda probe: probe.order, reverse = False ):
            style = "background: red" if sensor.is_active( ) else "background: white"
            state = sensor.timestamp.strftime( "%a %b %d %I:%M:%S %p" ) if sensor.timestamp else "Inactive"
            self.write( "<tr style=\"{}\">".format( style ) )
            self.write( "<td>{}</td>".format( state ) )
            self.write( "<td>{}</td>".format( sensor ) )
            self.write( "<td>{}</td>".format( sensor.date_back( ) ) )
            self.write( "</tr>" )
        self.write( "</tbody>" )
        self.write( "</table>" )
        self.write( "<br>" )
        self.write( self.service_status( ).decode( ).replace( "\n", "<br>" ) )

def signal_handler( sig, frame ):
    logger.critical( " graceful exit ... " )
    Sensor.save_state( )
    GPIO.cleanup( )
    sys.exit( 0 )

try:
    logger = logging.getLogger( 'Security Monitor' )
    logger.setLevel( logging.INFO )
    handler = logging.handlers.SysLogHandler( address = ( 'localhost', 514 ), facility = logging.handlers.SysLogHandler.LOG_DAEMON )
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
