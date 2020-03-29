# Project 1

Web Programming with Python and JavaScript

## Description

For this project I wanted to build a book review web application that lets users review a book they have read or lookup
reviews and ratings before starting to read it. This web application also uses APIs provided by Goodreads.com to get more ratings to help the user make a dission to read a book. A user would have to crate an account and login to be able to search for a book. Once the user finds the book he is looking for he could click on it from the table to view more details about it and only allowed to rate and review a book once.

## Folder Structure

    .
    |-- scripts
        |-- create.py       # A script that creates the tables in the database
        |-- import.py       # A script that imports the book from the csv file 'books.csv'
        |-- books.csv       # A csv file containing 5000 diffrent books to be imported into the database
    |-- templates
        |-- book.html       # html file that displays the book details page
        |-- error.html      # html file that indicates an error happened with a message
        |-- layout.html     # html file that has the main structure of the html pages
        |-- login.html      # html file that displays the login page
        |-- search.html     # html file that lets users search for books and show them in a table
        |-- signup.html     # html file that displays the signup page
    |-- application.py      # Flask application that controls when to render pages and add/search the database
    |-- README.md           # The file you are reading right now
    |-- requirements.txt    # Required packages to be installed to your computer

## Instructions to run

- pip3 install -r requirements.txt
- flask run
- open browser on <http://localhost:5000>
