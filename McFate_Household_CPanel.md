# Backup \_Archived\_EMail_ from Mark's MacBook

This button completes step 4 in the documented workflow for archival of PDF files created from email
messages (mailboxes) on Mark's MacBook.  
The affected Mail.app mailboxes include:

  * mark@TamaToledo.net
  * summitt.dweller@gmail.com
  * mcfatem@grinnell.edu
  * iowa.landmark.60@gmail.com
  * toledowieting@gmail.com
  * *mark@TamaToledo.org*
  * *mark.mcfate@iCloud.com* 
  * *mark@SummittServices.com*
  * *admin@SummittServices.com *
  * *summittservices60@gmail.com*  

The first 5 accounts listed above are processed automatically in Step 2 below.  The rest must be processed manually as documented in Step 3 below.

## Workflow
  1. In the Mail.app select all flagged messages and copy them to On My Mac | Previously_Flagged for safe-keeping.
  2. Launch **EMail Archiver Pro**
  This will process all messages in the first 5 mail accounts listed above. The PDFs and attachment folders created by **EMail Archiver Pro** are stored in subfolders of
  /Users/mark/Documents/ \_Archived\_EMail_  .
  3. Still in the Mail.app, select all but Junk and Deleted messages in the mailboxes that are NOT in italics (the last 5), click File | Export As PDF..., and send the exports to /Users/mark/Documents/\_Archived\_Email_.
  4.   Launch **Finder** then **Go** | **Connect To Server** to mount
  smb://mark@fileserver/files/ as /Volumes/files
  5. Return to this app, *McFate Household CPanel*, and click the **Backup
  \_Archived\_EMail_ from Mark's MacBook** button.
  This runs a command of the form...
  ```
  /usr/bin/python /Users/mark/Projects/Python/home_backup/home_backup/home_backup.py
  /Users/mark/Documents/_Archived_EMail_ /Volumes/files/STORAGE/_MAIL
  -c ./rsync_config.properties -m mark@tamatoledo.net -l ./home_backup.log
  --remove -b -d
  ```
  ...and moves the PDFs and corresponding folders from Steps 2 and 3 to
  **//fileserver/files/STORAGE/\_MAIL/\_Archived\_EMail\_** using rsync.
  5. Follow-up by deleting all files and folders from
  /Users/mark/Documents/\_Archived\_EMail_.

  Repeat every 2-4 weeks.

# Post //fileserver/files/STORAGE/? Files to Solr

Use this command to run a Solr POST command of the form...
```
/opt/solr/bin/post -c fs-core /files/STORAGE/<folder>
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
