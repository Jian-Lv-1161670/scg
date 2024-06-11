# scg

COMP636_S1 Assessment - Design Decisions

Design Decisions Discussion

Application Design and Development Decisions
When designing and developing our application, we carefully considered several design options to ensure an efficient and user-friendly experience. Our decisions were based on factors such as usability, scalability, and maintainability.


During the design and development of the application, several key decisions were made to ensure a robust, user-friendly, and maintainable system. Here, we discuss the rationale behind these decisions, particularly focusing on routing, templates, and navigation.



Routing and Navigation
We opted for a RESTful routing structure to organize our application's endpoints logically. Each route corresponds to a specific resource or functionality within the application. For example:

/customer/<customer_id>/edit allows users to edit customer information.
/booking/add handles the addition of new bookings.
We also implemented a navigation system that provides intuitive access to different sections of the application. This includes navigation links in the header or sidebar, allowing users to easily switch between pages.

Templating and Layout
We adopted a modular approach to templating, utilizing Jinja2 templates to generate HTML dynamically. This allowed us to maintain consistency across pages while still customizing content based on user interactions.

For example, when editing customer information, we opted to use the same template for both viewing and editing, dynamically enabling input fields for editing through conditional statements. This approach minimized duplication of code and simplified maintenance.

Data Handling
In terms of data handling, we utilized both GET and POST methods to request and send data.

GET requests were used for retrieving data, such as fetching customer details or booking information.
POST requests were employed for submitting form data, such as adding new bookings or updating customer information.
These decisions were made to ensure secure and efficient data transmission between the client and server, as well as to adhere to RESTful principles.


Templates
Separate Templates for Viewing and Editing:
Advantage: Clear separation of concerns, reduced complexity, and easier maintenance.
Example: Separate templates for viewing customer information and editing customer details.
Reason: Simplifies code logic by avoiding conditional statements for toggling between modes and provides flexibility in designing different interfaces.
Navigation and Layout
Modular Layout:
Used a modular approach with distinct templates for different functionalities.
Example: Separate templates for booking forms, customer lists, and reports.
Reason: Enhances readability, maintainability, and scalability of the application.






Database Design
SQL Statements
1，The SQL statement that creates the customer table and defines its fields/columns is as follows:

CREATE TABLE IF NOT EXISTS `customers` (
  `customer_id` INT NOT NULL AUTO_INCREMENT,
  `firstname` VARCHAR(45) NULL,
  `familyname` VARCHAR(60) NOT NULL,
  `email` VARCHAR(255) NULL,
  `phone` VARCHAR(12) NULL,
  PRIMARY KEY (`customer_id`)
);

2，The line of SQL code that sets up the relationship between the customer and booking tables is:

CONSTRAINT `customer`
  FOREIGN KEY (`customer`)
  REFERENCES `scg`.`customers` (`customer_id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION

3，The lines of SQL code that insert details into the sites table are:

INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('P1', '5');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('P4', '2');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('P2', '3');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('P5', '8');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('P3', '2');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('U1', '6');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('U2', '2');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('U3', '4');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('U4', '4');
INSERT INTO `sites` (`site_id`, `occupancy`) VALUES ('U5', '2');

4，To record the time and date a booking was added to the database, we would need to add a new column to the bookings table:

To record the time and date a booking was added, we would add the following fields to the bookings table:

Table Name: bookings
New Columns:
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP



5， If the ability for customers to make their own bookings was added, two different changes would be needed to the data model:

We would need to add a new table to store booking details made by customers, with appropriate foreign key constraints to link it to the customers table.
We would also need to modify the existing bookings table to differentiate between bookings made by customers and those made by administrators, possibly by adding a new column indicating the booking source.

1，Add a User Authentication System:

New Table: users
user_id INT NOT NULL AUTO_INCREMENT
username VARCHAR(50) NOT NULL
password_hash VARCHAR(255) NOT NULL
customer_id INT
PRIMARY KEY (user_id)
FOREIGN KEY (customer_id) REFERENCES customers (customer_id)

2，Modify the Bookings Table:

New Column: created_by INT NOT NULL
Foreign key linking to the users table to track which user made the booking.






设计决策

讨论设计 和开发应用时 所做的决策
what design option you weighted up

why you designed your app the way that you did,

your descision about the routes, tempaltes, navigation, broad layout, etc, that you made.


For example, when the edit button is clicked on a page, 
does that open a different template for editing or does it use the same template with IF statements to enable the editing? 
Did you use GET or POST to request and send data, and how and why? These are two examples, 
you do not have to include them in your own discussion. You will have considered many design possibilities;
 write in plain language about your own personal decisions.

Database questions: Refer to the supplied scg_local.sql file to answer the following questions:
1.
What SQL statement creates the customer table and defines its fields/columns? (Copy and paste the relevant lines of SQL.)
2.
Which line of SQL code sets up the relationship between the customer and booking tables?
3.
Which lines of SQL code insert details into the sites table?
4.
Suppose that as part of an audit trail, the time and date a booking was added to the database needed to be recorded. What fields/columns would you need to add to which tables? Provide the table name, new column name and the data type. (Do not implement this change in your app.)
5.
Suppose the ability for customers to make their own bookings was added. Describe two different changes that would be needed to the data model to implement this. (Do not implement these changes in your app.)


