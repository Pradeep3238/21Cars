CREATE TABLE cardetails (
    car_id INT AUTO_INCREMENT PRIMARY KEY,
    carname VARCHAR(50),
    features TEXT,
    ownerdetails VARCHAR(100),
    location varchar(25),
    image_url varchar(255),
    FOREIGN KEY (car_id) REFERENCES accounts(id)
);