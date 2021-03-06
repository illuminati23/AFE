#!/usr/bin/python
# encoding: utf-8
import argparse, shlex, sys, urllib2, time, SocketServer, base64, os, ntpath
from common import Server, version, ServerHandler
from basecmd import *
from subprocess import call
from modules import Modules
from exploit import Exploits

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


class Menu(BaseCmd):

    def __init__(self, conn, session):
        BaseCmd.__init__(self, session)
        self.connected = conn
        self.session = session
        if (conn == 1):
            self.prompt = "*Afe/menu$ "
        else:
            self.prompt = "Afe/menu$ "

    def do_back(self, _args):
        """
Return to home screen
        """
        return -1


    def do_devices(self, _args):
        """
List Connected Devices 
        """
        call(["adb", "devices"])

    def do_modules(self, args):
	    """
Shows all the modules present in the Modules directory
	    """
	    subconsole = Modules(self.connected, self.session)
	    subconsole.cmdloop()
	
    def do_exploit(self, args):
	    """
Shows all the modules present in the Modules directory
	    """
	    subconsole = Exploits(self.connected, self.session)
	    subconsole.cmdloop()
	
    def do_query(self, args):
        """
Query the TCP Server!
    Usage: query <arguments> [<arguments> ...]
For getting the content providers, which are exported or not
    Usage: query exported
For querying the content providers,
    Usage: query "[Arguments]"
           [Arguments]:
           get --url   = The content provider URI
               --proj  = The Projections, seperated by comma
           app <appname space> = Give the app name space to check if the app exists or not
     Example Usage:
           query "get --url content://dcontent/providers"
           query "app com.afe.socket"
        """
        try:
            parser = argparse.ArgumentParser(prog="query", add_help = False)
            parser.add_argument('argu', metavar="<arguments>", nargs='+')
            parser.add_argument('--file', '-f', metavar = '<file>', dest='file')
            splitargs = parser.parse_args(shlex.split(args))
            sendbuf = ' '.join(splitargs.argu)
            sendbuf1 = sendbuf.strip()
            if(self.connected == 1):
                if(splitargs.file):
                    if(os.path.isfile(splitargs.file)):
                        print path_leaf
                        print "Inside"
                        fin = open(splitargs.file, "rb")
                        binary_data = fin.read()
                        fin.close()
                        b64_data = base64.b64encode(binary_data)
                        print b64_data
                        count = 0
                        line =""
                        if len(b64_data) > 100000000000000:
                            for b in b64_data:
                                if count < 1000:
                                    line += b
                                    count += 1
                                else:
                                    print "Here"
                                    self.session.sendData( "file " + line + "\n")
                                    resp = self.session.receiveData()
                                    print resp
                                    count = 0
                                    line = ""
                        else:
                            print "Here 1"
                            self.session.sendData( "file " + b64_data + "\n")
                            resp = self.session.receiveData()
                            print resp
                            
                        self.session.sendData("file [end]" + "\n")
                        print "Data Sent !!"
                    else:
                        print "False"
                self.session.sendData(sendbuf + "\n")
                resp = self.session.receiveData()
                print resp
            else:
                print "**Not connected to the AFE SERVER App !"
        except:
            pass
    def do_serve(self, args):
	    """
Starts a Server in Localhost with your predefined port!
    Usage: serve -p --port <port>
           Default Port is 8080
	    """
            try:
                parser = argparse.ArgumentParser(prog="serve", add_help = False)
                parser.add_argument('--port', '-p', metavar = '<port>', type=int)
                splitargs = parser.parse_args(shlex.split(args))
                if (splitargs.port):
                    PORT = int(splitargs.port)
                else:
                    PORT = 8080
                
                Handler = ServerHandler
                httpd = SocketServer.TCPServer(("", PORT), Handler)
                print "serving at port ", PORT
                httpd.serve_forever()
            except KeyboardInterrupt:
                httpd.server_close()
                print time.asctime(), "Server Stops - At this point"
            except:
                pass
