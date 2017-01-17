# Sync comments from header files to source code files.
## This program also can update file comments for a directory.
I wrote this program to sync all the method comments from .h to .cpp because I don't want to copy comments from .h to .cpp every time I changed something in the .h. 

### If you want to write different comments in source file, this program does not help unless you only want to update file comments.

#Requirements
* Python 3 is required. No planning to support Py2.

#How to Use
Download and unzip the files.

    cd sync-comments-h2s-master
    sudo ./sh2s

If you do not see any error, you are done.

###Now, go to the folder that contains your .h/.cpp files and run "sh2s".
##Example

Sync comments from .h to .cpp

    sh2s
OR  Sync comments from .hh to .cc

    sh2s -extension hh|cc
OR  Sync comments from .h to .cpp and update file comments.

    sh2s -fc author|Bill
OR  Update file comments only.

    sh2s -fc-only author|Bill


#Options

    -extension hh|cc
The default pair is h|cpp

update file comments. This program will always attempt to add "@file filename.xxx"
Use the following command to add extra comments

    -fc author:Bill|date:2017.01.01

The following arguments will only update the file comments without modifing any other comments in any file.

    -fc-only author:Bill|date:2017.01.01

###Example result for update file comments
    /**
     * @file test_sh2s.cpp
     * @author Bill
     * @date 2017.01.01
     */

#Limitation
* Does not support template yet.
* No much tests have been done for C.




