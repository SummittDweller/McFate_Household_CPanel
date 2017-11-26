#!/usr/bin/env python

"""
MyCPanel.py - McFate household control panel

Python2 script to automate McFate household automation and operations.

Basic GUI with command-line option lifted from https://acaird.github.io/2016/02/07/simple-python-gui
source.

"""

import os.path
import argparse
import tkFileDialog
import fileinput
import StringIO
from lxml import etree
from Tkinter import *
from shutil import copyfile


def get_IOH_filename(input_file_name):
    """ IOH now treats an underscore here as indication of a language, like _english, so change any/all underscores to dashes! """
    input_file_name.replace("_", "-")
    parts = os.path.split(input_file_name)
    return parts[0] + "/IOH-" + parts[1]


def gui():
    """make the GUI version of this command that is run if no options are
    provided on the command line"""
    
    def button_transform_callback():
        """ what to do when the "Transform" button is pressed """
        xmlfile = entry.get()
        
        if xmlfile.rsplit(".")[-1] != "xml":
            statusText.set("Filename must have a .xml extension!")
            message.configure(fg="red")
            return
        else:
            
            """ clean up the XML first """
            x = fileinput.input(xmlfile, inplace=1)
            for line in x:
                line = line.replace('&lt;', '<')
                line = line.replace('&gt;', '>')
                print line,
            x.close()
            
            """ make it pretty """
            parser = etree.XMLParser(resolve_entities=False, strip_cdata=False)
            document = etree.parse(xmlfile, parser)
            document.write(xmlfile, pretty_print=True, encoding='utf-8')
            
            """ now transform it """
            IOH_xml = xsl_transformation(xmlfile)
            if IOH_xml is None:
                statusText.set("Error transforming file `{}'.".format(xmlfile))
                message.configure(fg="red")
                return
            
            output_file_name = get_IOH_filename(xmlfile)
            
            ioh_file = open(output_file_name, "w")
            if ioh_file:
                ioh_file.write(str(IOH_xml))
                ioh_file.close()
                statusText.set("Output is in {}".format(output_file_name))
                message.configure(fg="dark green")
                entry.delete(0, END)
                entry.insert(0, output_file_name)
            
            else:
                statusText.set("File `{}' could not be opened for output.".format(output_file_name))
                message.configure(fg="red")
    
    def button_hms_callback():
        """ what to do when the "Convert hh:mm:ss..." button is pressed """
        
        xmlfile = entry.get()
        
        if xmlfile.rsplit(".")[-1] != "xml":
            statusText.set("Filename must have a .xml extension!")
            message.configure(fg="red")
            return
        else:
            
            x = fileinput.input(xmlfile, inplace=1)
            for line in x:
                matched = re.match(r'(.*)(\d\d:\d\d:\d\d\.\d\d)(.*)', line)
                if matched:
                    hms = matched.group(2)
                    h, m, s = hms.split(':')
                    sec = str(int(h) * 3600 + int(m) * 60 + float(s))
                    line = line.replace(hms, sec)
                print line,
            
            x.close()
            statusText.set("hh:mm:ss values in `{}' have been converted to seconds.".format(xmlfile))
            message.configure(fg="dark green")
    
    def button_format_callback():
        """ what to do when the "Format" button is pressed """
        
        xmlfile = entry.get()
        
        if xmlfile.rsplit(".")[-1] != "xml":
            statusText.set("Filename must have a .xml extension!")
            message.configure(fg="red")
            return
        
        else:
            """ identify all the speaker tags """
            q = etree.parse(xmlfile)
            speaker_tags = q.findall('.//speaker')
            speakers = dict()
            num = 1
            
            for tag in speaker_tags:
                if tag.text:
                    full = tag.text.strip()
                    first, rest = full.split(' ', 1)
                    first = first.strip()
                    if first not in speakers:
                        speakers[first] = {'number': num, 'class': "<span class='oh_speaker_" + str(num) + "'>",
                                           'full_name': full}
                        num += 1
            
            """ examine each cue, identify speakers in the transcript.text and modify that text accordingly """
            cue_tags = q.findall('.//cue')
            for tag in cue_tags:
                t = tag.find('transcript')
                text = t.text.replace('\n', ' ').replace('  ', ' ').replace(' :', ':').replace(' |', '|')
                
                words = text.split()
                t.text = ''
                count = 0
                speakers_found = []
                
                for word in words:
                    if word.endswith('|'):
                        speaker = word.strip('|')
                        if speaker in speakers:
                            if count > 0:
                                t.text += '</span></span>'
                            # t.text += "<span class='oh_speaker'>" + speaker + ': ' + speakers[speaker]['class']
                            t.text += speakers[speaker]['class'] + speaker + ": " + "<span class='oh_speaker_text'>"
                            if speaker not in speakers_found:
                                speakers_found.append(speaker)
                            count += 1
                        else:
                            statusText.set("Referenced speaker '" + speaker + "' has no corresponding <speaker> tag!")
                            message.configure(fg="red")
                            return
                    else:
                        t.text += ' ' + word
                
                t.text += '</span></span>'
                
                """ now build a proper <speaker> tag from the references found, and apply it """
                speaker_tag = ''
                for speaker in speakers_found:
                    speaker_tag += speakers[speaker]['full_name'] + ' & '
                speaker_tag = speaker_tag.strip(' & ')
                
                t = tag.find('speaker')
                t.text = speaker_tag
            
            q.write(xmlfile)
            
            statusText.set("Speaker formatting for transcript `{}' is complete.".format(xmlfile))
            message.configure(fg="dark green")
    
    def button_reformat_callback():
        """ what to do when the "Reformat" button is pressed """
        
        xmlfile = entry.get()
        if xmlfile.rsplit(".")[-1] != "xml":
            statusText.set("Filename must have a .xml extension!")
            message.configure(fg="red")
            return
        
        IOH_xmlfile = get_IOH_filename(xmlfile)
        copyfile(xmlfile, IOH_xmlfile)
        
        """ make it pretty """
        parser = etree.XMLParser(resolve_entities=False, strip_cdata=False)
        document = etree.parse(IOH_xmlfile, parser)
        document.write(IOH_xmlfile, pretty_print=True, encoding='utf-8')
        
        """ identify all the speaker tags """
        q = etree.parse(IOH_xmlfile)
        speaker_tags = q.findall('.//speaker')
        speakers = dict()
        num = 1
        
        for tag in speaker_tags:
            if tag.text:
                full = tag.text.strip()
                if ' ' not in full:
                    first = full
                else:
                    first, rest = full.split(' ', 1)
                
                first = first.strip()
                if first not in speakers:
                    speakers[first] = {'number': num, 'class': "<span class='oh_speaker_" + str(num) + "'>",
                                       'full_name': full}
                    num += 1
        
        """ examine each cue, identify THE speaker and modify the cue accordingly """
        cue_tags = q.findall('.//cue')
        speakers_found = []
        
        for tag in cue_tags:
            s = tag.find('speaker')
            if ' ' not in s.text.strip():
                first = s.text.strip()
            else:
                first, rest = s.text.strip().split(' ', 1)
            first = first.strip()
            if first not in speakers_found:
                speakers_found.append(first)
            t = tag.find('transcript')
            if t.text is None:
                statusText.set("Transcript has no text at source line " + str(t.sourceline) + "!")
                message.configure(fg="red")
                return
            
            text = t.text.replace('\n', ' ').replace('  ', ' ').replace(' :', ':').replace(' |', '|')
            t.text = ''
            try:
                t.text += speakers[first][
                              'class'] + first + ": " + "<span class='oh_speaker_text'>" + text + '</span></span>'
            except KeyError:
                statusText.set("Transcript 'KeyError' at source line " + str(t.sourceline) + "! Please investigate.")
                message.configure(fg="red")
                return
        
        q.write(IOH_xmlfile)
        entry.delete(0, END)
        entry.insert(0, IOH_xmlfile)
        
        statusText.set("Speaker reformatting for transcript `{}' is complete.".format(IOH_xmlfile))
        message.configure(fg="dark green")
    
    def button_browse_callback():
        """ What to do when the Browse button is pressed """
        filename = tkFileDialog.askopenfilename()
        entry.delete(0, END)
        entry.insert(0, filename)
    
    # Transform any XML with a XSLT
    # Lifted from https://gist.github.com/revolunet/1154906
    
    def xsl_transformation(xmlfile, xslfile="./Transform_InqScribe_to_IOH.xsl"):
        
        xsl = open(xslfile)
        if xsl:
            xslt = xsl.read()
        else:
            statusText.set("XSLT file `{}' could not be opened.".format(xslfile))
            message.configure(fg="red")
        
        xslt_tree = etree.XML(xslt)
        transform = etree.XSLT(xslt_tree)
        
        xml = open(xmlfile)
        if xml:
            xml_contents = xml.read()
        else:
            statusText.set("XML file `{}' could not be opened.".format(xmlfile))
            message.configure(fg="red")
        
        f = StringIO.StringIO(xml_contents)
        doc = etree.parse(f)
        f.close()
        transform = etree.XSLT(xslt_tree)
        result = transform(doc)
        
        return result
    
    # ------------------------------------------------
    
    root = Tk()
    root.title("Transform_InqScribe_to_IOH v1.0")
    root.geometry("1000x275")
    frame = Frame(root)
    frame.pack()
    
    statusText = StringVar(root)
    statusText.set(
        "Press Browse button or enter XML file path then press the Transform..., Convert..., or Format... button as needed.")
    
    label = Label(root, text="Transform, Convert or Format an Oral History XML file:")
    label.pack(padx=10)
    entry = Entry(root, width=80, justify='center')
    entry.pack(padx=10)
    separator = Frame(root, height=2, bd=1, relief=SUNKEN)
    separator.pack(fill=X, padx=10, pady=5)
    
    button_browse = Button(root, text="Browse", command=button_browse_callback)
    button_transform = Button(root, text="Transform InqScribe to IOH XML", command=button_transform_callback)
    button_hms = Button(root, text="Convert hh:mm:ss to Seconds", command=button_hms_callback)
    button_format = Button(root, text="Format Speakers", command=button_format_callback)
    button_reformat = Button(root, text="Reformat an Old Transcript", command=button_reformat_callback)
    button_exit = Button(root, text="Exit", command=sys.exit)
    button_browse.pack()
    button_transform.pack()
    button_hms.pack()
    button_format.pack()
    button_reformat.pack()
    button_exit.pack()
    
    separator = Frame(root, height=2, bd=1, relief=SUNKEN)
    separator.pack(fill=X, padx=10, pady=5)
    
    message = Label(root, textvariable=statusText)
    message.pack(padx=10, pady=5)
    
    mainloop()


def command_line(args):
    """ Run the command-line version
    if args.output is None:
      args.output = get_IOH_filename(args.input)
  
    table_contents = read_csv(args.input)
  
    if write_table(args.output, table_contents):
      print "rst table is in file `{}'".format(args.output)
    else:
      print "Writing file `{}' did not succeed.".format(args.output)
    """


def get_parser():
    """ The argument parser of the command-line version """
    parser = argparse.ArgumentParser(description=('convert csv to rst table'))
    
    parser.add_argument('--input', '-F',
                        help='name of the intput file')
    
    parser.add_argument('--output', '-O',
                        help=("name of the output file; " +
                              "defaults to <inputfilename>.rst"))
    return parser


# -----------------------------------------------------

if __name__ == "__main__":
    """ Run as a stand-alone script """
    
    parser = get_parser()  # Start the command-line argument parsing
    args = parser.parse_args()  # Read the command-line arguments
    
    if args.input:  # If there is an argument,
        command_line(args)  # run the command-line version
    else:
        gui()  # otherwise run the GUI version
        
        
# ================================= Old backup.d code follows =====================================

""" backup.d/backup.py

Use this Python script from the command line (terminal) in combination with restore.py.  This script will create a
 *.tar.gz containing an SQL dump and a tar of vars.site_path files.

This script must exist in a ./backup.d directory inside your project directory.  Corresponding scripts vars.py and
restore.py must also exist in this same directory and vars.py must be modified to define your site and user
parameters BEFORE performing any backup/restore operations.

Backups will be stored in and restored from a .data directory off the parent directory where the project lives.

The typical project tree structure looks like this...

project/
  file1
  file2
  file3
  backup.d/
    backup.py
    restore.py
    vars.py
  .data/
    project.tar.gz_timestamp
    other_data1
    other_data2

"""

"""
from colorama import init
from colorama import Style, Fore, Back
import vars
import os
import subprocess
import sys
import glob
from datetime import datetime

init()  # for Colorama

# Get the current (working) directory and verify that necessary parts are in place.
cwd = os.getcwd()
print Style.BRIGHT + Fore.GREEN + "\nThe current (working) directory is '" + cwd + "'." + Style.RESET_ALL

if (not os.path.isdir("backup.d")):
  print Style.BRIGHT + Fore.RED + "\nPlease change directories.  The required backup.d/ directory does NOT exist.  This process is terminated.\n" + Style.RESET_ALL
  exit(1)

if (not os.path.isdir(".data")):
  print Style.BRIGHT + Fore.RED + "\nThe required .data/ directory does NOT exist.  Let's make one now.\n" + Style.RESET_ALL
  os.mkdir(".data", 0776)

# Get the current time and build a destination file name
timeStamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
file = vars.backup + "_" + str(timeStamp)
destination = "/home/" + vars.user + "/" + file
userAtServer = vars.user + "@" + vars.server
local = cwd + "/.data/" + file

# Determine the user's home directory so we can check for a public SSH key.
homeDir = os.path.expanduser("~")
pubKey = homeDir + "/.ssh/id_rsa.pub"

# If the user of this script has an id_rsa|id_rsa.pub (private|public) key pair append the public key the remote user's ~/.ssh/authorized_keys.
if os.path.isfile(pubKey):
  args = [ "ssh-copy-id", "-i", pubKey, userAtServer ]
  print Style.BRIGHT + "\nLaunching remote " + Fore.GREEN + " ".join(args) + Fore.RESET + " to establish key file authentication..."
  try:
    subprocess.check_output(args, stderr=subprocess.STDOUT)
  except subprocess.CalledProcessError as e:
    print e.output
else:
  print Style.BRIGHT + Fore.RED + "\nNo ~/.ssh/id_rsa.pub public key found so the " + userAtServer + " password may be required several times. " + Fore.RESET

# Cleanup the remote server before beginning
command = "rm -f /home/" + vars.user + "/" + vars.server + ".sql /home/" + vars.user + "/" + vars.backup
args = [ "ssh", userAtServer, command ]
print Style.BRIGHT + "\nLaunching " + Fore.GREEN + " ".join(args) + Fore.RESET + " to clean up... " + Style.RESET_ALL
error = subprocess.check_call(args)

# Define a 'drush cr all' command to flush the cache
command = "cr all"
args = [ "ssh", userAtServer, vars.drush, vars.drush_alias, command ]
print Style.BRIGHT + "\nLaunching remote " + Fore.GREEN + " ".join(args) + Fore.RESET + " to clear the cache"
error = subprocess.check_call(args)

# Try 'drush sql-dump' instead of 'drush ard', it's easier to control
command = "sql-dump --result-file=" + vars.site_path + "/files/" + vars.server + ".sql --skip-tables-key=common"
args = [ "ssh", userAtServer, vars.drush, vars.drush_alias, command ]
print Style.BRIGHT + "\nLaunching " + Fore.GREEN + " ".join(args) + Fore.RESET +" to dump the database... " + Style.RESET_ALL
error = subprocess.check_call(args)

# Follow up with a 'tar' command under better control
skip = [ "*/.git/*", "config_*", "*/files/css/*", "*/js/*", "*/php/*", "*services.yml", "*settings.php", "*/.data/*" ]
exclude = " --exclude=".join(skip)
# command = "tar -czvf " + destination + " -C " + vars.site_path + " . /home/" + vars.user + "/*.sql --exclude=" + exclude
command = "tar -czvf " + destination + " -C " + vars.site_path + " . --exclude=" + exclude
args = [ "ssh", userAtServer, command ]
print Style.BRIGHT + "\nLaunching " + Fore.GREEN + " ".join(args) + Fore.RESET + " to create a backup... " + Style.RESET_ALL
error = subprocess.check_call(args)

# No problems thus far?...rsync the file back to the host
args = [ "rsync", "-aruvi", userAtServer + ":" + destination, local ]
print Style.BRIGHT + "\nRunning " + Fore.GREEN + ' '.join(args) + Fore.RESET + " to copy the backup to your host..."  + Style.RESET_ALL
error = subprocess.check_call(args)

# If stick is mounted, copy the backup there too
if os.path.isdir(vars.stick):
    args = ["rsync", "-aruvi", local, vars.stick]
    print Style.BRIGHT + "\nRunning " + Fore.GREEN + ' '.join(args) + Fore.RESET + " to copy the backup to your mounted " + vars.stick + " volume..."  + Style.RESET_ALL
    error = subprocess.check_call(args)
    print Style.BRIGHT + Fore.GREEN + "\nContents of " + vars.stick + ": " + Style.RESET_ALL
    print "  " + "\n  ".join(glob.glob(vars.stick + "/*"))
    print "\n\n"
else:
    print Style.BRIGHT + "\nMount a portable drive at " + vars.stick + " and use "
    print Fore.GREEN + "  'rsync -aruvi " + local + " " + vars.stick + "' " + Fore.RESET + "to copy the backup there.\n\n" + Style.RESET_ALL

"""
