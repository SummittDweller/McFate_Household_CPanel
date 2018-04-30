#!/usr/bin/env python

"""
McFate_Household_CPanel.py - McFate household control panel

Python2 script to control McFate household automation and operations.

Basic GUI with command-line option lifted from https://acaird.github.io/2016/02/07/simple-python-gui
source.

"""

import os.path
import glob
import argparse
import tkFileDialog
import subprocess
import spur
import webbrowser
import json
from Tkinter import *  # use 'brew install homebrew/dupes/tcl-tk' to install

import fileinput
import StringIO
# from lxml import etree
from shutil import copyfile


def listdir_nohidden(path):
  return glob.glob(os.path.join(path, '*'))


def gui():
  """make the GUI version of this command that is run if no options are provided on the command line"""
  
  def button_help_callback():
    """ what to do when the "Help" button is pressed """
    
    filename = "./McFate_Household_CPanel.md.html"
    webbrowser.open('file://' + os.path.realpath(filename))
    statusText.set("The help file, 'McFate_Household_CPanel.md.html' should now be visible in a new browser tab.")
    message.configure(fg="dark green")
  
  def button_solr_post_callback():
    """ what to do when the "Post //fileserver/files/? Files to Solr" button is pressed """
    
    target = entry.get()
    statusText.set("/opt/solr/bin/post for {} is running on fileserver...".format(target))
    message.configure(fg="red")
    message.update()
    
    fileserver = "192.168.1.24"
    
    shell = spur.SshShell(hostname="fileserver", username="mark", missing_host_key=spur.ssh.MissingHostKey.warn)
    target_path = "/files/{}".format(target)
    result = shell.run(["/opt/solr/bin/post", "-c", "fs-core", target_path])
    # result = shell.run(["ls", "-al", "/."])
    
    statusText.set("/opt/solr/bin/post on fileserver is complete with a return code of {}".format(result.return_code))
    message.configure(fg="dark green")
    
    # print result.output
  
  def button_solr_query_callback():
    """ what to do when the "Query Solr on Fileserver" button is pressed """
    
    target = entry.get()
    statusText.set("Solr query {} is running on fileserver...".format(target))
    message.configure(fg="red")
    message.update()
    
    shell = spur.SshShell(hostname="fileserver", username="mark", missing_host_key=spur.ssh.MissingHostKey.warn)
    query = "http://localhost:8983/solr/fs-core/select?wt=json&fl=id&q={}".format(target)
    result = shell.run(["curl", query])
    # result = shell.run(["ls", "-al", "/."])
    
    d = json.loads(result.output)
    r = d.get('response')
    docs = r.get('docs')
    numFound = r.get('numFound')
    msg = "Solr query is complete with {} documents found.".format(numFound)
    if numFound > 0:
      msg = msg + "  They include:\n\n"
      for rd in docs:
        msg = msg + rd.get('id') + "\n"
    
    statusText.set(msg)
    message.configure(fg="dark green")
  
  def button_backup_email_callback():
    """ what to do when the "Backup _Archived_EMail_" button is pressed """
    
    """ check if _Archived_EMail_ exists and has files, and if /Volumes/files is mounted """
    directory = "/Users/mark/_Archived_EMail_"
    volume = "/Volumes/files"
    
    if not os.path.isdir(directory):
      statusText.set("Error: The {} directory does not exist!".format(directory))
      message.configure(fg="red")
    elif listdir_nohidden(directory) == []:
      statusText.set("Warning: The {} exists but it is empty!  Nothing to do here.".format(directory))
      message.configure(fg="red")
    elif not os.path.isdir(volume):
      statusText.set("Error: The {} volume is not mounted!".format(volume))
      message.configure(fg="red")
    else:
      statusText.set("home_backup.py is running...")
      message.configure(fg="red")
      message.update()
      
      bashCommand = "/usr/bin/python /Users/mark/Projects/Python/home_backup/home_backup/home_backup.py /Users/mark/_Archived_EMail_/ /Volumes/files/STORAGE/_MAIL/ -c ./rsync_config.properties -m mark@tamatoledo.net -l ./home_backup.log --remove -b -d"
      process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
      output, error = process.communicate()
      
      statusText.set(
        "home_backup.py is finished. You should take steps to clean out {} and the 'For Archival' mailbox.".format(
          directory))
      message.configure(fg="dark green")
  
  def button_backup_NEAT_Exports_callback():
    """ what to do when the "Backup NEAT Exports" button is pressed """
    
    """ check if iMac500GB exists and has files, and if /Volumes/files is mounted """
    directory = "/Volumes/iMac500GB"
    volume = "/Volumes/files"
    
    if not os.path.isdir(directory):
      statusText.set("Error: The {} directory does not exist!".format(directory))
      message.configure(fg="red")
    elif listdir_nohidden(directory) == []:
      statusText.set("Warning: The {} exists but it is empty!  Nothing to do here.".format(directory))
      message.configure(fg="red")
    elif not os.path.isdir(volume):
      statusText.set("Error: The {} volume is not mounted!".format(volume))
      message.configure(fg="red")
    else:
      statusText.set("home_backup.py is running...")
      message.configure(fg="red")
      message.update()
      
      bashCommand = "/usr/bin/python " \
                    "/Users/markmcfate/Projects/Python/home_backup/home_backup/home_backup.py " \
                    "/Volumes/iMac500GB/ /Volumes/files/NEAT/NEAT_Exports -c " \
                    "./rsync_config.properties -m mark@tamatoledo.net " \
                    "-l ./home_backup.log -e .* --remove -b -d"
      process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
      output, error = process.communicate()
      
      statusText.set(
        "home_backup.py to NEAT is finished. You should take steps to clean out {} if necessary.".format(directory))
      message.configure(fg="dark green")
    
  
  def button_browse_callback():
    """ What to do when the Browse button is pressed """
    filename = tkFileDialog.askopenfilename()
    entry.delete(0, END)
    entry.insert(0, filename)
  
  # ------------------------------------------------
  
  root = Tk()
  root.title("McFate Household CPanel v1.0")
  root.geometry("1000x350")
  frame = Frame(root)
  frame.pack()
  
  statusText = StringVar(root)
  statusText.set("Browse to open a file OR choose an operation to perform.")
  
  label = Label(root, text="Input or selected file/folder:")
  label.pack(padx=10)
  entry = Entry(root, width=80, justify='center')
  entry.pack(padx=10)
  separator = Frame(root, height=2, bd=1, relief=SUNKEN)
  separator.pack(fill=X, padx=10, pady=5)
  
  button_browse = Button(root, text="Browse", command=button_browse_callback)
  button_backup_email = Button(root, text="Backup _Archived_EMail_ from Mark's MacBook",
                               command=button_backup_email_callback)
  button_backup_NEAT_Exports = Button(root, text="Backup NEAT Exports from Mark's iMac",
                               command=button_backup_NEAT_Exports_callback)
  button_solr_post = Button(root, text="Post //fileserver/files/? Files to Solr",
                            command=button_solr_post_callback)
  button_solr_query = Button(root, text="Query Solr on fileserver", command=button_solr_query_callback)
  button_help = Button(root, text="Help", command=button_help_callback)
  button_exit = Button(root, text="Exit", command=sys.exit)
  button_browse.pack()
  button_backup_email.pack()
  button_backup_NEAT_Exports.pack()
  button_solr_post.pack()
  button_solr_query.pack()
  button_help.pack()
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
