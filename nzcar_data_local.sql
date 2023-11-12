CREATE SCHEMA IF NOT EXISTS nzcar;
USE nzcar;

CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('customer', 'staff', 'admin') NOT NULL
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone_number VARCHAR(20) NOT NULL,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

CREATE TABLE IF NOT EXISTS staff (
    staff_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone_number VARCHAR(20) NOT NULL,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

CREATE TABLE rentalcars (
    car_id INT AUTO_INCREMENT PRIMARY KEY,
    car_model VARCHAR(255) NOT NULL,
    registration_number VARCHAR(20) NOT NULL,
    year INT NOT NULL,
    seating_capacity INT NOT NULL,
    rental_per_day DECIMAL(10, 2) NOT NULL,
    availability BOOLEAN NOT NULL DEFAULT TRUE,
    car_image VARCHAR(255)
);



INSERT INTO users (username, password, role)
VALUES
    ('john_doe', '$2b$12$fW7rvG5ilKsnHPM5YcfO/uBYlOsdCuJvrZNDw01WbdIvQsVGgar1i', 'customer'),
    ('jane_smith', '$2b$12$EGdNEeq0m6a/5Daz3AOVO.vZl6jpQ8IZD7d.KrBMjc5eNf8JOhA4.', 'customer'),
    ('michael_johnson', '$2b$12$XLH7U6lEm2xLwKRnDlvnx.o66oMsYA2deUkqo5j4PlwYDVohMThni', 'customer'),
    ('emily_williams', '$2b$12$wuMiQDgUxMhuYmh2x/lGdeTBIq1iaPLT45.tHCCKL4PMlnwrPncku', 'customer'),
    ('david_lee', '$2b$12$vgqsScdbP4LRMVPbzAaLB.f1FSsoba87Zmgu.6GUaGqHpDn.C.eP2', 'customer'),
    ('mary_johnson', '$2b$12$Ux6IMUYoW1rDH8LcpEnvOO7FOGZH.fo1wfVwOMRaX.aaNaScbQQe6', 'staff'),
    ('robert_williams', '$2b$12$1pQ0sZLEHZNJngmws7Ak1.ZeMWhillCCHy48W8EIKj4IEguBGIaE6', 'staff'),
    ('sarah_lee', '$2b$12$aw/NgBx.kArv7HU5KIEoMu45SumtsNHSzSjydydwJXhrvXdlRlKkm', 'staff'),
    ('admin_user', '$2b$12$GcchWMi3PKE5D.xLxJMiOOq7OrSHL0zlYx2Y9V8uEMC4Ei7mHZu36', 'admin')
;


INSERT INTO customers (name, address, email, phone_number, user_id)
VALUES
  ('John Doe', '123 Main St, City', 'john@example.com', '+123456789', 1),
  ('Jane Smith', '456 Oak Ave, Town', 'jane@example.com', '+987654321', 2),
  ('Michael Johnson', '789 Elm Rd, Village', 'michael@example.com', '+246813579', 3),
  ('Emily Williams', '987 Pine Ln, County', 'emily@example.com', '+135792468', 4),
  ('David Lee', '321 Oak St, Town', 'david@example.com', '+246801357', 5)
;

INSERT INTO staff (name, address, email, phone_number, user_id)
VALUES
  ('Mary Johnson', '789 Elm Rd, Village', 'mary@example.com', '+246813579', 6),
  ('Robert Williams', '987 Pine Ln, County', 'robert@example.com', '+135792468', 7),
  ('Sarah Lee', '456 Oak St, City', 'sarah@example.com', '+123456789', 8),
  ('Admin User', 'Admin Address', 'admin@example.com', '+123456789', 9)
;

INSERT INTO rentalcars (car_model, registration_number, year, seating_capacity, rental_per_day,availability,car_image)
VALUES
  ('Toyota Camry', 'ABC123', 2020, 5, 50.00,TRUE, '1691052900.037761car.jpeg'),    
  ('Honda Civic', 'XYZ789', 2019, 4, 45.00, TRUE, '1691052900.037761car.jpeg'),     
  ('Ford Mustang', 'MNO46', 2018, 4, 60.00,TRUE, '1691052900.037761car.jpeg'),    
  ('Chevrolet Suburban', 'PQR79', 2022, 7, 80.00,TRUE, '1691052900.037761car.jpeg'),  
  ('Volkswagen Golf', 'DEF122', 2017, 4, 40.00, TRUE,'1691052900.037761car.jpeg'),   
  ('Tesla Model S', 'JKL456', 2023, 4, 120.00,TRUE, '1691052900.037761car.jpeg'),   
  ('Nissan Altima', 'GHI789', 2019, 5, 55.00,TRUE, '1691052900.037761car.jpeg' ),    
  ('Mercedes-Benz E-Class', 'MNO13', 2021, 5, 90.00,TRUE, '1691052900.037761car.jpeg'),  
  ('BMW X5', 'PQR46', 2020, 5, 85.00, TRUE,'1691052900.037761car.jpeg'),      
  ('Audi Q5', 'ABC567', 2019, 5, 70.00,TRUE, '1691052900.037761car.jpeg'),     
  ('Hyundai Elantra', 'XYZ79', 2021, 4, 40.00, TRUE,'1691052900.037761car.jpeg'),  
  ('Kia Sorento', 'MNO456', 2018, 7, 75.00,TRUE, '1691052900.037761car.jpeg'),   
  ('Ford Focus', 'PQR789', 2017, 4, 35.00, TRUE,'1691052900.037761car.jpeg'),     
  ('Toyota RAV4', 'DEF123', 2022, 5, 65.00, TRUE,'1691052900.037761car.jpeg'),   
  ('Honda Accord', 'JKL45', 2020, 5, 55.00, FALSE,'1691052900.037761car.jpeg'),    
  ('Chevrolet Cruze', 'GI789', 2019, 5, 45.00,FALSE, '1691052900.037761car.jpeg'),  
  ('Nissan Rogue', 'MNO123', 2021, 5, 60.00, FALSE,'1691052900.037761car.jpeg'),    
  ('Subaru Outback', 'PQR456', 2020, 5, 70.00,FALSE, '1691052900.037761car.jpeg'),  
  ('Ford Explorer', 'JKL789', 2018, 7, 75.00, FALSE,'1691052900.037761car.jpeg'),    
  ('Hyundai Tucson', 'MNO234', 2022, 5, 65.00, FALSE,'1691052900.037761car.jpeg'),   
  ('Kia Forte', 'PQR567', 2020, 4, 40.00, FALSE,'1691052900.037761car.jpeg')   
;

