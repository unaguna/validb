SET @old_autocommit=@@autocommit;

--
-- Current Database: `dev`
--

DROP DATABASE IF EXISTS `dev`;

CREATE DATABASE `dev` DEFAULT CHARACTER SET utf8mb4;

USE `dev`;

SET autocommit=@old_autocommit;
