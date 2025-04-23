function numCourses() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheets = ss.getSheets();
  var logSheet = ss.getSheetByName("Log");
  var abbreviationsRange = logSheet.getRange("A2:A" + logSheet.getLastRow());
  var abbreviations = abbreviationsRange.getValues();
  var providersRange = logSheet.getRange("F2:F" + logSheet.getLastRow());
  var providers = providersRange.getValues();

  // Clear existing data in column H
  logSheet.getRange("I2:I" + logSheet.getLastRow()).clear();

  for (var i = 0; i < sheets.length; i++) {
    var sheet = sheets[i];
    var sheetName = sheet.getName();

    // Find the matching abbreviation for the current sheet
    var abbreviationIndex = abbreviations.findIndex(row => row[0] === sheetName);

    if (abbreviationIndex != -1) {
      // If a matching abbreviation is found
      var provider = providers[abbreviationIndex][0];

      // Get the data range based on the provider
      var dataRange;
      if (provider === "apm") {
        dataRange = sheet.getRange("A2:A");
      } else {
        dataRange = sheet.getRange("B2:B");
      }

      // Get the unique values in the data range
      var uniqueValues = getUniqueValues(dataRange);

      // Write the count of unique values to column H
      logSheet.getRange(abbreviationIndex + 2, 9).setValue(uniqueValues.length - 1);
    } else {
      Logger.log("No matching abbreviation found for sheet '" + sheetName + "'.");
    }
  }
}

function getUniqueValues(range, filterOpen) {
  var values = range.getValues();
  var uniqueValues = [];
  var seenValues = {};

  for (var i = 0; i < values.length; i++) {
    var value = values[i][0]; // Assuming the unique values are in the first column
    var status = values[i][1]; // Assuming the status is in the second column

    // Consider only rows where column B equals "Open" if filterOpen is true
    if (!filterOpen || status === "Open") {
      if (!seenValues[value]) {
        uniqueValues.push(value);
        seenValues[value] = true;
      }
    }
  }

  return uniqueValues;
}


function TotalCounts() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheets = ss.getSheets();
  var logSheet = ss.getSheetByName("Log");
  var abbreviationsRange = logSheet.getRange("A2:A" + logSheet.getLastRow());
  var abbreviations = abbreviationsRange.getValues();
  var providersRange = logSheet.getRange("F2:F" + logSheet.getLastRow());
  var providers = providersRange.getValues();

  // Clear existing data in column H
  logSheet.getRange("H2:H" + logSheet.getLastRow()).clear();

  for (var i = 0; i < sheets.length; i++) {
    var sheet = sheets[i];
    var lastRow = sheet.getLastRow();
    var sheetName = sheet.getName();

    // Find the matching abbreviation for the current sheet
    var abbreviationIndex = abbreviations.findIndex(row => row[0] === sheetName);

    if (abbreviationIndex != -1) {
      // If a matching abbreviation is found
      var provider = providers[abbreviationIndex][0];
      Logger.log(provider)
      // If the provider is "apm", count rows where "Activity Status" is "Open"
      if (provider === "apm") {
        var dataRange = sheet.getDataRange();
        var values = dataRange.getValues();
        var openRowCount = 0;
        for (var j = 1; j < values.length; j++) {
          if (values[j][1] === "Open") {
            openRowCount++;
          }
        }
        logSheet.getRange(abbreviationsRange.getCell(abbreviationIndex + 1, 1).getRow(), 8).setValue(openRowCount);
      } else {
        // If the provider is not "apm", simply count all rows
        logSheet.getRange(abbreviationsRange.getCell(abbreviationIndex + 1, 1).getRow(), 8).setValue(lastRow);
      }
    } else {
      Logger.log("No matching abbreviation found for sheet '" + sheetName + "'.");
    }
  }
}

