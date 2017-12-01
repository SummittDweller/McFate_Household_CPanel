# Backup \_Archived\_EMail_ from Mark's MacBook

This button completes step 4 in the documented workflow for archival of PDF files created from email
messages (mailboxes) on Mark's MacBook.
The affected Mail.app mailboxes in  /Users/mark/Library/V3 may include:

  * mark@TamaToledo.net
  * mark@TamaToledo.org
  * summitt.dweller@gmail.com
  * mcfatem@grinnell.edu
  * iowa.landmark.60@gmail.com
  * mark.mcfate@iCloud.com 
  * toledowieting@gmail.com
  * mark@SummittServices.com
  * admin@SummittServices.com 
  * summittservices60@gmail.com  

## Workflow
  1. In the Mail.app select all messages then  **Message** | **Apply Rules**.
  Be sure to do this for all inboxes and sent mail!
  The rules move all selected, applicable messages (more than 2 weeks old) to
  mailbox: On My Mac /
  For_Archival  /Users/mark/Library/V3/ 5375A271-44A6-4E8E-
B19B-E8EC0EA9260C 
  2. Launch **EMail Archiver Pro**
  This will process all messages in the aforementioned For_Archival mailbox
  converting each to PDF along with a corresponding folder of attachments.  The
  PDFs and attachment folders are stored in
  /Users/mark/Documents/ \_Archived\_EMail_  .
  3.   Launch **Finder** then **Go** | **Connect To Server** to mount
  smb://mark@fileserver/files/ as /Volumes/files
  4. Return to this app, *McFate Household CPanel*, and click the **Backup
  \_Archived\_EMail_ from Mark's MacBook** button.
  This runs a command of the form...
  ```
  /usr/bin/python /Users/mark/Projects/Python/home_backup/home_backup/home_backup.py
  /Users/mark/Documents/_Archived_EMail_ /Volumes/files/STORAGE/_MAIL
  -c ./rsync_config.properties -m mark@tamatoledo.net -l ./home_backup.log
  --remove -u -d
  ```
  ...and moves the PDFs and corresponding folders from Step 2 to
  **//fileserver/files/STORAGE/\_MAIL/\_Archived\_EMail\_/For_ Archival.mbox/_year_/_month_** using rsync.
  5. Follow-up by deleting all files and folders from
  /Users/mark/Documents/\_Archived\_EMail_ and all mail messages from the
  'On My Mac' **For_Archival** mailbox.

  Repeat every 2-4 weeks.

# Post //fileserver/files/STORAGE/? Files to Solr

Use this command to run a Solr POST command of the form...
```
/opt/solr/bin/post -c fs-core /files/<folder>
```
...on //fileserver/files where the target _folder_ is specified using the **Browse** button and field.

Note that you may be unable to use the **Browse** button to select a target folder but you must make sure the target field contains a string matching one of these choices:
  * STORAGE/_AUDIO
  * ~~STORAGE/_BINARIES~~
  * STORAGE/_CODE
  * STORAGE/_DATA
  * STORAGE/_DOCUMENTS
  * STORAGE/_HOME_BACKUP
  * STORAGE/_IMAGES
  * STORAGE/_MAIL
  * STORAGE/_MISC
  * STORAGE/_PHOTOS
  * STORAGE/_VIDEOS
  * GENEALOGY
  * NEAT
  * ~~RESCUE~~


  Or, leave the field blank to choose ALL folders under //fileserver/files (not recommended!).
