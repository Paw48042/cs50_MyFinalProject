# 291 ONLINE LIBRARY
#### Video Demo : <https://youtu.be/ScZZgrcXkcw>
#### Description :

### **Understanding**
Hi, I'm Pawee Prempulsawad from Thailand and I work in Infantry battalion. In my workplace there's a library, with lots of FM(Field Manual) and it's keep missing. Recently, I've found out recently that anyone can go and grab it! anytime!. So, I've decide to build an webapp that let you come and borrow books and also let you know that which book is available or which book is borrowed.

### **Process**
The Process of this library is like this. You Register -> Login -> Borrow -> Return or Extend the borrowing period , and then repeat. But in the webapp I've made there's no return function because It'll be weird if users can return the book online. So I decide to let the staff do the return part in the actual world. Also, The ability to change book status back from borrowed or extended to available is only the battalion staff things in backend.

Here's some of the code that I've write so far

### **Register**
First is register. This page require your Firstname, Lastname, Email, Username, Password (and also re type password). Constraint is that if users use username that already exist, users will get an alert that this username have already been used. same as an email. After user finish the register part, they'll get a confirmation Email just to recheck that your email is correct because they'll have to use in the borrow part(user 'll get an Email as a ticket to show to battalion staff to get the book)

### **Login and Forgot Password**
    Login is meant to log you in the system, this page is log you in to the index page by query through users table to check if username and password is exist and match. If everythings is going well, you'll be login to the homepage. Next is "Forgot Password" Page if you type down username and email, it'll query through your users table, decipher the password and sent the password through your regsiter email.

### **Homepage**
This page will show all of your book that have not returned yet, By querying and joining data in the database. The data that shown on the homepage is transaction_id book_id book_name borrow_date return_date status (borrowed or extended)

### **Lookup**

This page let you search your book through table 'book_data' to see if this book is existed, available, borrowed or extended. You can find the book you want through book id, or code(like categories : FM is stand for field manual Joint Publication is for Joint combat KM is stand like a internal knowledge management)
, you can also find a book through publish year or authors. By the way, in this web app. There's only 100 books for a sample data.

### **Borrow**

Borrow page let you borrow the book by searching through the book_data first (just like lookup). After searching through book_data and get the table of books. You can click "Borrow" button at the most right of the table, After you click the button, the query will sent to the database and redirect you to the homepage with a alert that says "you have successfully borrow a book". The web app will also sent an Email to borrower, so that they can use that email as a ticket to show when they've come and get the book from battalion staff.

### **Extend**

Extend page let you extend the borrow time by 7 days, Every user will get 1 extend chance from the start. extend function is to check if this user have an extend chance left (chance >= 1). If they have, minus the chance by 1 and extend the borrow period by 7 days. if chance == 0 then it's mean that they have to return the book first to get the extend chance back.

### **Project.db**
This file contains 3 tables for the library
Users Table : store the user id password and personal information
Book_data Table : store the data of the book in infantry battalion
History : Record transaction of borrowed book

### app.py
This is where all the function above (Register, login, lookup, borrow, extend livesin)

### Html Page
This is the User Interface of the program, which combine html, jinja, css. html stores in project/templates css and image stuff store in project/static