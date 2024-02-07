# Rosters webscraper

## Run script

```shell

./run_webscraper.sh

```

## Exit codes

| Code | Description                                           |
|------|-------------------------------------------------------|
| 0    | Outcome: Success                                      |
| 1    | Fail: Uncaught error                                  |
| 2    | Fail: Caught error (e.g. could not log in, could not find rosters page) |
| 3    | Outcome: No roster records found (did not fail)       |
| 4    | Skipped                                               |
| 5    | Not configured                                        |
