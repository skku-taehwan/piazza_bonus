# Piazza bonus web crawler
Piazza is a free online gathering place where students can ask, answer, and explore 24/7, under the guidance of their instructors. https://piazza.com/

This is a crawler for piazza to extract students who are endorsed for good questions, notes, and discussions. It also extracts the number of times endorsed and the total.

### environment
- Ubuntu 20.04.3 LTS 
- python 3.8.10
- recommanded chrome version
    -  Version 96.0.4664.110 (Official Build) (64-bit)
- chrome driver
    - you have to download chromedriver which matches your chrome version and place it in the working directory where main.py is located. https://sites.google.com/chromium.org/driver/
### launch
- `python3 [piazza_class_URL] [piazza_ID] [piazza_PASSWD]`
- time : 3183 seconds, 53 minutes
### output
- csv file
    - StudentName : [bonus id list] [list count]

### future upgrade
- ...
