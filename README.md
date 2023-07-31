# Finder
## Function
For testing purposes only dating site. After user registration to the DB. Other users in defined circle around user are shown according to setting (age, sex, range). User can deside to swipe or match them. If both user are matched, then it is possible to chat online.

__PLEASE TAKE NOTE:__ This app is only for learning purposes and could contain bugs. Also there is lot of possibilities to upgrade it!!

![Setting page where user can set up gender, age, range of circle and so on.](https://github.com/JiriSvacek/Finder/blob/master/pics/setting.PNG)
## Stack
* Flask
* MySQL
* JS
* SocketIO
  
![Matched page, where matched users can chat to each other](https://github.com/JiriSvacek/Finder/blob/master/pics/matched_chat.PNG)

## Test it on: [Python anywhere*](https://JiriSvacek.eu.pythonanywhere.com )

*Web-sockets on python anywhere are not supported!!! Thus the **chatting** option is **slow**. It takes ~30 sec to load actual data, it is not immediate. [In app.py parameter allow_upgrades should be True for normal function](https://github.com/JiriSvacek/Finder/blob/db825a9287312168a16b2372cebe9b1083dfc32a/app.py#L33)

*Saving of images is not working as request are not supported.
