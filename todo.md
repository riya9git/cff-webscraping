## Some things I want to do
- [ ] Add commandline argument for local export vs. Gsheets
    - [ ] Add commandline argument logic
- [ ] Add custom errors to Selenium (cf. [2. of other todo](#212024-todo))
    - Should fail gracefully at every step if a certain element doesn't exist, will be useful for debugging too
    - [ ] APM
    - [ ] Rec1


## General
- error handling
    - Fix redwood city
    - Fix dublin
    - Fix fremont (there's no rosters but only attendance -- only first and last name of student or something like that)
        - Want to get counts
    - Fix hayward -- 
    - Distinguish failed Selenium from 0 records (Hayward I think?)
- Gsheets integration

## 2/1/2024 Todo

1. [X] Make apm grab all seasons instead of Winter/Fall as is the current implementation. It will be easier to filter all the data once it is online, and will result in a more stable code.
2. [ ] Investigate some cities that are not currently working due to non-standard implementations of APM/REC1 frameworks. Determine whether I can make a small adjustment to accommodate these cities, or whether it is better to get the data manually, also depending on city priority.
3. [ ] Improve logging logic: particularly, the script should distinguish between the Selenium logic failing (clicking on a missing element, etc.) and the logic working and finding 0 elements. Also consider edge cases that may result in logs that are inaccurate. Basically the goal here is to make the logs as robust and reliable as possible.
    - [ ] APM
    - [ ] Rec1
4. [ ] Once the logs have been verified, write them to the "Logs" tab of "DataManagement Scripts" so all users can see the output of the log. Be sure to add datetime in there to make it very easy to see when the last time the script was run.

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
3. [ ] Generate logs to indicate if a portal was not accessible etc.
  - [ ] Show each portal tried and success or failure, and number of entries in the roster for it.
  - [ ] Inform the user - to go to 'Data Management' and run 'Get City Roster' Script from the CFF menu.
  - [ ] Look into cities
    - [ ] Fremont
    - [ ] Dublin
    - [ ] Hayward
    - [ ] Redwood City
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


