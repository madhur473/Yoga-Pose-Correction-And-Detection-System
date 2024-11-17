create database yoga_db;
use yoga_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    firstname VARCHAR(50) NOT NULL,
    lastname VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);


//add to table for the streaks functionality 
ALTER TABLE users
ADD COLUMN streak INT DEFAULT 0,
ADD COLUMN last_login DATETIME;

//Viewing all the cols and rows
Select * from users
