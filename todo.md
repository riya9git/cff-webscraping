## Some things I want to do
- [ ] Add commandline argument for local export vs. Gsheets
    - [ ] Add commandline argument logic
    - [ ] Argument for headless
- [ ] Logging
    - [X] Figure out how to append to "Log" Gsheet
    - [X] Figure out return states
        - [X] Rec1 shows 0 sign-up classes but APM doesn't
        - [X] Distinguish between script failure and 0 classes
    - [ ] Add counts
        - [ ] Number of courses (courses is generally preferred name)
        - [ ] Number of sign-ups
- [ ] Get counts from Fremont
- [ ] Parallelize! 

## Scraping:
1. [X] Set up Python Google sheets API
  - [X] Figure out OAuth
  - [X] Import from sheet
  - [X] Export to sheet
2. [X] Get config from Data Management sheet
  - [ ] accept it as a command line argument.
  - [X] Add headless??
  - [X] In: Use 'City List' tab in 'Data Management' Sheet, to
    - [X] Get list of active cities and their portal urls & credentials
      - [X] Read in sheets data to use in webscraper
    - [X] Location to send roster data.
    - [X] create a set of INPUTs, Product and Test, similar to input sheet. (?)
  - [X] Out: Obtain the roster csv and upload to this directory.
3. [X] Generate logs to indicate if a portal was not accessible etc.
  - [X] Show each portal tried and success or failure,
  - [ ] Number of entries in the roster for it.
  - [ ] Inform the user - to go to 'Data Management' and run 'Get City Roster' Script from the CFF menu.
  - [X] Look into cities
    - [X] Fremont
    - [X] Dublin
    - [X] Hayward
    - [X] Redwood City
5. An Appscript built into 'Data Management' - called 'Get City Roster'
  - [ ] This script will collect the csv data in specified folder from 'City List' tab
  - [ ] Build a dictionary and add it to AllRoster, per product
    - Need a way to tag Products in City Camps, with ProductDocIds in AllRoster
    - Log if product is not found
    - Add rows as needed
  - [ ] For Students previously added, but no longer found in city rosters, set the Withdrawn column as Y (or something)
    - Note: AllRoster has In-person and Online tabs, though city rosters, are probably only In-Person
  - [ ] This script should finally run the 'Update Registration Counts' script as well (this maybe currently broken)

## Import/Export:
- Create a <Popup popupid='upload-csv', which will find and upload a file from local drive into memory.
    Note: there is a feature being built in branch  remotes/origin/upload-file, to upload a file to Firebase storage.
          Not sure if it can be used.
- This file will be Tracks.csv, Courses.csv or Products.csv for now [or Json objects, just exported, see below]
- Convert each row to a valid Json object, similar to' manage_db.py make json' and add to *Edits collection, with IMPORT tag.
    Currently only Modification and Addition are supported.
    [need to think about overwrites]
- Do not allow Import/Export operations if any modification/additions are present on a per *Edits basis.
- The imported object, may be a new addition, or update of an existing object, based on docId.
- Allow edits of these records, so any issues can be fixed - should work as is, based on current code.
   Rest of the operation should just work, that is 'Approve' should copy/add the objects to the respective parent collections.
   Discard should delete the object.
Export:
    - In the item Table's first column, provide an Export checkBox, and in the Header, Export All.
    - Provide a button above the Table to 'Export Selected Items', this is to avoid adding/deleting objects just by
        checking a checkbox, especially the export all checkbox, as these are expensive operations.
    - Once exported, add the objects to the appropriate *Edits collections, same as 'Save' or 'Apply to All'
        Note: Same functionality won't work, as save doesn't happen if nothing is changed, so skip this check.
    - Tag these records as 'Export'
    - On export, ask the user where to save the file, and save both .csv and .json versions of the file.
