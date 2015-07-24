# -*- coding: utf-8 -*-
#!/usr/bin/env python
# Copyright (C) 2014-2015 - Regional Norte - UdelaR - (<http://www.unorte.edu.uy>).
#                           Miguel Pertusatti - miguel@unorte.edu.uy
# This file is part of Printemail.
#
#    Printemail is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Printemail is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Revisa correos electrónicos recibidos y envía archivos PDF adjuntos a cola de impresión"""

import os
import sys
import email
import errno
import mimetypes

from optparse import OptionParser
import ConfigParser
import MySQLdb
import magic
import logging
import pdb

def BuscarImpresoras(Servidor,Usuario,DB,Clave,Identificador):
    db1 = MySQLdb.connect(Servidor,Usuario,DB,Clave)
    # prepare a cursor object using cursor() method
    cursor = db1.cursor()
    # execute SQL query using execute() method.
    cursor.execute("SELECT localpart from users where realname = '{0}'".format(Identificador))
    resul=[]
    for row in cursor.fetchall() :
        resul.append(row[0])    
    # Fetch a single row using fetchone() method.
    #data = cursor.fetchone()
    # print "Database version : %s " % data
    #print "lista-1"
    #print "lista-2"
    # disconnect from server
    db1.close()
    return resul

def extrer_adjunto(msgfile,destino):
    fp = open(msgfile)
    msg = email.message_from_file(fp)
    fp.close()

    counter = 1
    remitente = msg['from'].split()[-1]
    for part in msg.walk():
        # multipart/* are just containers
        if part.get_content_maintype() == 'multipart':
            continue
        # Applications should really sanitize the given filename so that an
        # email message can't be used to overwrite important files
        filename = part.get_filename()
        if not filename:
            ext = mimetypes.guess_extension(part.get_content_type())
            if not ext:
                # Use a generic bag-of-bits extension
                ext = '.bin'
            filename = 'part-%03d%s' % (counter, ext)
        counter += 1
        fp = open(os.path.join(destino, filename), 'wb')
        fp.write(part.get_payload(decode=True))
        fp.close()
        
def main():
    parser = OptionParser(usage="""\
Revisa correos electrónicos recibidos y envía archivos PDF adjuntos a cola de impresión.

Uso: %prog [options]
""")
    '''
    parser.add_option('-d', '--directory',
                      type='string', action='store',
                      help="""Unpack the MIME message into the named
                      directory, which will be created if it doesn't already
                      exist.""")
    '''
    parser.add_option('-c', '--config',
                      type='string', action='store',
                      help="""Config File.""")
    opts, args = parser.parse_args()
    if not opts.config:
        config_file = "printemail.conf"
    else:
        config_file = opts.config
        
    try:
        f = open(config_file, 'r')
    except IOError:
        print 'cannot open', config_file
        parser.print_help()
        sys.exit(1)
    f.close()
    
    pdb.set_trace()
    Config = ConfigParser.ConfigParser()
    Config.read(config_file)
    Config.sections()
    # ['Others', 'SectionThree', 'SectionOne', 'SectionTwo']
    #options = Config.options(section)
    dict1 = {}
    # dict1[option] = Config.get(section, option)
    Servidor=Config.get('Base', 'Servidor')
    DB=Config.get('Base', 'DB')
    Usuario=Config.get('Base', 'Usuario')
    Clave=Config.get('Base', 'Clave')
    Identificador=Config.get('Correo', 'Identificador')
    Buzones=Config.get('General', 'Buzones')
    Bandeja=Config.get('General', 'Bandeja')
    Seplista=Config.get('Correo', 'Seplista')
    Sepcorreo=Config.get('Correo', 'Sepcorreo')
    Temporales=Config.get('General', 'Temporales')
    Cups=Config.get('General', 'Cups')
    Cupsport=Config.get('General', 'Cupsport')
    #Logslevel=Config.get('General', 'Logslevel')
    #Logsdir=Config.get('General', 'Logsdir')
    #logger = logging.getLogger('printemail')
    #hdlr = logging.FileHandler(Logsdir)
    #formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    #hdlr.setFormatter(formatter)
    #logger.addHandler(hdlr) 
    #logger.setLevel(logging.INFO)
    #mime = magic.Magic(mime=True)
    while (1==1):
        # identificar impresoras
        Impresoras=BuscarImpresoras(Servidor,Usuario,DB,Clave,Identificador)
        #if not Impresoras:
        #    logger.info('No se encontraron Impresoras')
        for impresora in Impresoras:
            # buscara archivos para imprimir en su cuenta
            cuenta_relacionada = impresora.replace(Seplista,Sepcorreo)
            carpeta_con_correos = Buzones+cuenta_relacionada+Bandeja
            #if not os.path.exists(carpeta_con_correos):
            #    logger.error('No existe carpeta con correos')
            for filename in os.listdir(carpeta_con_correos):
                extrer_adjunto(carpeta_con_correos+'/'+filename,Temporales)
                for adjunto in os.listdir(Temporales):
                    if magic.from_file(adjunto, mime=True) == 'application/pdf':
                        # [-3:] in ['pdf','PDF']
                        # imprimir
                        orden='lp -h {0}:{1} -d {2} {3}'.format(Cups,Cupsport,impresora,Temporales+'/'+adjunto)
                        os.system(orden)
                        #comprobar
                        #acumular
                        #borrar
                    else:
                        # borrar
                        continue
                # borrarcorreo
                print 'nada'
    
    '''
    if not opts.directory:
        parser.print_help()
        sys.exit(1)

    try:
        msgfile = args[0]
    except IndexError:
        parser.print_help()
        sys.exit(1)

    try:
        os.mkdir(opts.directory)
    except OSError as e:
        # Ignore directory exists error
        if e.errno != errno.EEXIST:
            raise
    '''

    
if __name__ == '__main__':
    main()
