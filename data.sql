CREATE DATABASE IF NOT EXISTS `pradeep`;
USE `pradeep`;

CREATE TABLE IF NOT EXISTS `accounts` (
	`id` int(11) NOT NULL,
  	`username` varchar(50) NOT NULL,
  	`password` varchar(255) NOT NULL,
  	`email` varchar(100) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB ;
