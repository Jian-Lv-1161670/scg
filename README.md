## COMP636_S1 Assessment

### Design Decisions

#### Overview
During the design and development of my project, I made several critical decisions to ensure the intuitive usability of the system's core functionalities. Additionally, I prioritized a clean and efficient page layout, followed by considerations for the system's scalability.

Here, I will discuss the rationale behind these decisions, particularly focusing on routing, templates, and navigation.
I opted for a RESTful routing structure to organize our application's endpoints logically 


#### RESTful routing structure


- Consistency: Different operations use consistent verbs and path formats, such as /customer to retrieve a list of customers,  /new_customer to create a new user, and customer/1665/ to retrieve information about a specific user.

- Readability: URL paths intuitively describe their operations and resources, making them easy for developers and users to understand.

- Maintainability: A logically structured path structure makes the application easier to maintain and expand.


#### Routes and Methods
- **GET Method:**
  - Used for fetching and displaying data.
  - Examples: Viewing customer details, booking information, and search results.
  - **Reason:** GET requests are cacheable, bookmarkable, and suitable for operations that do not modify the server state.

- **POST Method:**
  - Used for submitting data to the server.
  - Examples: Adding new bookings, editing customer information.
  - **Reason:** POST requests securely transmit data in the request body, handle larger data payloads, and are appropriate for operations that modify server state.


#### User Experience
- **Simple Interface:** Keep the interface simple, avoiding excessive elements and complicated operations.

- **Consistent Design:** Use consistent fonts, colors, and layout styles to make it easier for users to become familiar with and use the system.
- **Examples:**  Integrate buttons for "Reports," "Delete," and "Edit" on both the user list and user search pages. This facilitates users' 
 - **Reason:** intuitive access to the desired pages and actions, enhancing overall usability.


#### Templates
- **Separate Templates for Viewing and Editing:**
  - **Advantage:** Clear separation of concerns, reduced complexity, and easier maintenance.
  - **Example:** Separate templates for viewing customer information and editing customer details. 
  - **Reason:** Simplifies code logic by avoiding conditional statements for toggling between modes and provides flexibility in designing different interfaces.

#### Navigation and Layout
- **Modular Layout:**
  - Used a modular approach with distinct templates for different functionalities.
  - **Example:** Separate templates for booking forms, customer lists, and reports.
  - **Reason:** Enhances readability, maintainability, and scalability of the application.



### Database Questions

#### 1. SQL Statement to Create Customer Table
```sql
CREATE TABLE IF NOT EXISTS `customers` (
  `customer_id` INT NOT NULL AUTO_INCREMENT,
  `firstname` VARCHAR(45) NULL,
  `familyname` VARCHAR(60) NOT NULL,
  `email` VARCHAR(255) NULL,
  `phone` VARCHAR(12) NULL,
  PRIMARY KEY (`customer_id`));

```

#### 2. Relationship Between Customer and Booking Tables
```sql
CONSTRAINT `customer`
    FOREIGN KEY (`customer`)
    REFERENCES `scg`.`customers` (`customer_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

```


#### 3. SQL Code to Insert Details into Sites Table

```sql
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

```


#### 4. Audit Trail for Booking
To record the time and date a booking was added, we would add the following fields to the `bookings` table:

**Table Name:** `bookings`

**New Columns:**
- `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

#### 5. Changes for Customer Self-Booking
To enable customers to make their own bookings, the following changes would be needed:

**Add a User Authentication System:**

**New Table:** `users`
- `user_id` INT NOT NULL AUTO_INCREMENT
- `username` VARCHAR(50) NOT NULL
- `password_hash` VARCHAR(255) NOT NULL
- `customer_id` INT
- PRIMARY KEY (`user_id`)
- FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`)

**Modify the Bookings Table:**

**New Column:** `created_by` INT NOT NULL
- Foreign key linking to the `users` table to track which user made the booking.


### Image Source:

The logo used in this web app is a custom design created by myself using Photoshop. It is stored in the file `logo2.png`, located in the `static/image` directory of the project. The purpose of incorporating this logo is to add a touch of vibrancy and liveliness to the overall interface.
  
![Logo](static/images/logo2.png)



