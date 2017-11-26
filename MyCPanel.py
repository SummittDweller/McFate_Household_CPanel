#!/usr/bin/env python

"""
MyCPanel.py - McFate household control panel

Python2 script to control McFate household automation and operations.

Basic GUI with command-line option lifted from https://acaird.github.io/2016/02/07/simple-python-gui
source.

"""

import os.path
import glob
import argparse
import tkFileDialog
import subprocess
import fileinput
import StringIO
# from lxml import etree
from Tkinter import *
from shutil import copyfile


def listdir_nohidden(path):
    return glob.glob(os.path.join(path, '*'))


def gui():
    """make the GUI version of this command that is run if no options are provided on the command line"""
    
    def button_backup_email_callback():
        """ what to do when the "Backup _Archived_EMail_" button is pressed """

        """ check if _Archived_EMail_ exists and has files, and if /Volumnes/files is mounted """
        directory = "/Users/mark/Documents/_Archived_EMail_"
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

            bashCommand = "/usr/bin/python /Users/mark/Projects/Python/home_backup/home_backup/home_backup.py /Users/mark/Documents/_Archived_EMail_/ /Volumes/files/STORAGE/_MAIL/ -c ./rsync_config.properties -m mark@tamatoledo.net -l ./home_backup.log --remove -u -d --date"
            process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()

            statusText.set("home_backup.py is finished. You should take steps to clean out {} and the 'For Archival' mailbox.".format(directory))
            message.configure(fg="dark green")

        # selected_file = entry.get()
        # statusText.set("File `{}' selected but this operation is currently undefined.".format(selected_file))
        # message.configure(fg="red")


        # if xmlfile.rsplit(".")[-1] != "xml":
        #     statusText.set("Filename must have a .xml extension!")
        #     message.configure(fg="red")
        #     return
        # else:
        #
        #     x = fileinput.input(xmlfile, inplace=1)
        #     for line in x:
        #         line = line.replace('&lt;', '<')
        #         line = line.replace('&gt;', '>')
        #         print line,
        #     x.close()
        #
        #     parser = etree.XMLParser(resolve_entities=False, strip_cdata=False)
        #     document = etree.parse(xmlfile, parser)
        #     document.write(xmlfile, pretty_print=True, encoding='utf-8')
        #
        #     IOH_xml = xsl_transformation(xmlfile)
        #     if IOH_xml is None:
        #         statusText.set("Error transforming file `{}'.".format(xmlfile))
        #         message.configure(fg="red")
        #         return
        #
        #     output_file_name = get_IOH_filename(xmlfile)
        #
        #     ioh_file = open(output_file_name, "w")
        #     if ioh_file:
        #         ioh_file.write(str(IOH_xml))
        #         ioh_file.close()
        #         statusText.set("Output is in {}".format(output_file_name))
        #         message.configure(fg="dark green")
        #         entry.delete(0, END)
        #         entry.insert(0, output_file_name)
        #
        #     else:
        #         statusText.set("File `{}' could not be opened for output.".format(output_file_name))
        #         message.configure(fg="red")

    
    # def button_hms_callback():
    #     """ what to do when the "Convert hh:mm:ss..." button is pressed """
    #
    #     xmlfile = entry.get()
    #
    #     if xmlfile.rsplit(".")[-1] != "xml":
    #         statusText.set("Filename must have a .xml extension!")
    #         message.configure(fg="red")
    #         return
    #     else:
    #
    #         x = fileinput.input(xmlfile, inplace=1)
    #         for line in x:
    #             matched = re.match(r'(.*)(\d\d:\d\d:\d\d\.\d\d)(.*)', line)
    #             if matched:
    #                 hms = matched.group(2)
    #                 h, m, s = hms.split(':')
    #                 sec = str(int(h) * 3600 + int(m) * 60 + float(s))
    #                 line = line.replace(hms, sec)
    #             print line,
    #
    #         x.close()
    #         statusText.set("hh:mm:ss values in `{}' have been converted to seconds.".format(xmlfile))
    #         message.configure(fg="dark green")
    #
    # def button_format_callback():
    #     """ what to do when the "Format" button is pressed """
    #
    #     xmlfile = entry.get()
    #
    #     if xmlfile.rsplit(".")[-1] != "xml":
    #         statusText.set("Filename must have a .xml extension!")
    #         message.configure(fg="red")
    #         return
    #
    #     else:
    #         """ identify all the speaker tags """
    #         q = etree.parse(xmlfile)
    #         speaker_tags = q.findall('.//speaker')
    #         speakers = dict()
    #         num = 1
    #
    #         for tag in speaker_tags:
    #             if tag.text:
    #                 full = tag.text.strip()
    #                 first, rest = full.split(' ', 1)
    #                 first = first.strip()
    #                 if first not in speakers:
    #                     speakers[first] = {'number': num, 'class': "<span class='oh_speaker_" + str(num) + "'>",
    #                                        'full_name': full}
    #                     num += 1
    #
    #         """ examine each cue, identify speakers in the transcript.text and modify that text accordingly """
    #         cue_tags = q.findall('.//cue')
    #         for tag in cue_tags:
    #             t = tag.find('transcript')
    #             text = t.text.replace('\n', ' ').replace('  ', ' ').replace(' :', ':').replace(' |', '|')
    #
    #             words = text.split()
    #             t.text = ''
    #             count = 0
    #             speakers_found = []
    #
    #             for word in words:
    #                 if word.endswith('|'):
    #                     speaker = word.strip('|')
    #                     if speaker in speakers:
    #                         if count > 0:
    #                             t.text += '</span></span>'
    #                         # t.text += "<span class='oh_speaker'>" + speaker + ': ' + speakers[speaker]['class']
    #                         t.text += speakers[speaker]['class'] + speaker + ": " + "<span class='oh_speaker_text'>"
    #                         if speaker not in speakers_found:
    #                             speakers_found.append(speaker)
    #                         count += 1
    #                     else:
    #                         statusText.set("Referenced speaker '" + speaker + "' has no corresponding <speaker> tag!")
    #                         message.configure(fg="red")
    #                         return
    #                 else:
    #                     t.text += ' ' + word
    #
    #             t.text += '</span></span>'
    #
    #             """ now build a proper <speaker> tag from the references found, and apply it """
    #             speaker_tag = ''
    #             for speaker in speakers_found:
    #                 speaker_tag += speakers[speaker]['full_name'] + ' & '
    #             speaker_tag = speaker_tag.strip(' & ')
    #
    #             t = tag.find('speaker')
    #             t.text = speaker_tag
    #
    #         q.write(xmlfile)
    #
    #         statusText.set("Speaker formatting for transcript `{}' is complete.".format(xmlfile))
    #         message.configure(fg="dark green")
    

    def button_browse_callback():
        """ What to do when the Browse button is pressed """
        filename = tkFileDialog.askopenfilename()
        entry.delete(0, END)
        entry.insert(0, filename)
    

    # ------------------------------------------------
    
    root = Tk()
    root.title("McFate Household CPanel v1.0")
    root.geometry("1000x275")
    frame = Frame(root)
    frame.pack()
    
    statusText = StringVar(root)
    statusText.set("Browse to open a file OR choose an operation to perform.")
    
    label = Label(root, text="Selected file:")
    label.pack(padx=10)
    entry = Entry(root, width=80, justify='center')
    entry.pack(padx=10)
    separator = Frame(root, height=2, bd=1, relief=SUNKEN)
    separator.pack(fill=X, padx=10, pady=5)
    
    button_browse = Button(root, text="Browse", command=button_browse_callback)
    button_backup_email = Button(root, text="Backup _Archived_EMail_ from Mark's MacBook", command=button_backup_email_callback)
    button_exit = Button(root, text="Exit", command=sys.exit)
    button_browse.pack()
    button_backup_email.pack()
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
        
        
