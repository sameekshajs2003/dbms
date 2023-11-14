create database covid;
use covid;


CREATE TABLE `admin` (
    `username` varchar(50) NOT NULL,
    `password` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    PRIMARY KEY (`username`)
);


CREATE TABLE `hospitaluser` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `hcode` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `password` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    PRIMARY KEY (`hcode`),
    INDEX `id` (`id`)
);

CREATE TABLE `user` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `srfid` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `email` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `dob_pass` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    PRIMARY KEY (`srfid`),
    INDEX `id` (`id`)
);


CREATE TABLE `hospitaldata` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `hcode` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `hname` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `normalbed` int(11) NOT NULL,
    `icubed` int(11) NOT NULL,
    `vbed` int(11) NOT NULL,
    PRIMARY KEY (`id`),
    INDEX `hcode` (`hcode`),
    CONSTRAINT `fk_hcode` FOREIGN KEY (`hcode`) REFERENCES `hospitaluser` (`hcode`)
);


CREATE TABLE `booking_patient` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `srfid` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `bedtype` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `hcode` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `spo2` int(11) NOT NULL,
    `pname` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `pphone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
    `paddress` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    PRIMARY KEY (`id`),
    INDEX `srfid` (`srfid`),
    INDEX `hcode` (`hcode`),
    CONSTRAINT `fk_srfid` FOREIGN KEY (`srfid`) REFERENCES `user` (`srfid`),
    CONSTRAINT `fk_hode` FOREIGN KEY (`hcode`) REFERENCES `hospitaluser` (`hcode`)
);

CREATE TABLE `trig` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `hcode` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `normalbed` int(11) NOT NULL,
    `icubed` int(11) NOT NULL,
    `vbed` int(11) NOT NULL,
    `querys` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `date` date NOT NULL,
    PRIMARY KEY (`id`),
    INDEX `hcode` (`hcode`),
    CONSTRAINT `fk_ode` FOREIGN KEY (`hcode`) REFERENCES `hospitaluser` (`hcode`)
);

RENAME TABLE trig TO status;


ALTER TABLE bookingpatient
ADD COLUMN dob VARCHAR(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;


SHOW TABLES;
describe hospitaldata;
show create table hospitaldata;
select * from hospitaluser;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `GetAllBookingPatients`()
BEGIN
    -- Select all rows from the bookingpatient table
    SELECT * FROM bookingpatient;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` FUNCTION `IsHCodeInHospitalUser`(hcode_to_check VARCHAR(20)) RETURNS tinyint(1)
BEGIN
    DECLARE is_present BOOLEAN;

    -- Check if the hcode exists in the hospitaluser table
    SELECT COUNT(*) INTO is_present
    FROM hospitaluser
    WHERE hcode = hcode_to_check;

    RETURN is_present;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `CheckHCodeExistence`(IN `hcode` VARCHAR(255), OUT `result` INT)
BEGIN
    DECLARE isHCodeExists BOOLEAN;
    -- Call the function to check if the 'hcode' exists
    SET isHCodeExists = IsHCodeInHospitalUser(hcode);
    IF isHCodeExists THEN
        SET result = 1;
    ELSE
        SET result = 0;
    END IF;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `DisplayHospitalDataWithTotalBeds`()
BEGIN
 CREATE TEMPORARY TABLE hospitaldata_results AS SELECT *, normalbed + icubed + vbed AS total_beds FROM hospitaldata;

    -- Select 'normalbed', 'icubed', and 'vbed' columns
    SELECT normalbed, icubed, vbed,hcode,id,hname FROM hospitaldata_results;

    -- Display the sum of 'normalbed', 'icubed', and 'vbed' in a separate row
    SELECT SUM(normalbed) AS 'Total Normal Beds', SUM(icubed) AS 'Total ICU Beds', SUM(vbed) AS 'Total Ventilator Beds'
    FROM hospitaldata_results;

    -- Clean up temporary table
    DROP TEMPORARY TABLE IF EXISTS hospitaldata_results;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `DisplayUsersNotInBookingPatient`()
BEGIN
    -- Create a temporary table to store the result of the join
    CREATE TEMPORARY TABLE tmpResult AS
    SELECT u.id, u.srfid, u.email
    FROM user u
    LEFT JOIN bookingpatient bp ON u.srfid = bp.srfid
    WHERE bp.id IS NULL;

    -- Select the rows from the temporary table
    SELECT * FROM tmpResult;

    -- Clean up temporary table
    DROP TEMPORARY TABLE IF EXISTS tmpResult;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `SelectHospitalUserData`()
BEGIN
    -- Declare variables to hold the results
    DECLARE hospitaluser_data CURSOR FOR SELECT * FROM hospitaluser;

    -- Create a temporary table with specific columns
    CREATE TEMPORARY TABLE hospitaluser_results AS
    SELECT id, hcode, email FROM hospitaluser;

    SELECT * FROM hospitaluser_results;

    -- Clean up temporary table
    DROP TEMPORARY TABLE IF EXISTS hospitaluser_results;
END$$
DELIMITER ;


DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `GetSeverePatients`()
BEGIN
    SELECT bp.pname, bp.srfid, hd.hcode, hd.hname
    FROM bookingpatient bp
    JOIN hospitaldata hd ON bp.hcode = hd.hcode
    WHERE bp.srfid IN (
        SELECT srfid
        FROM bookingpatient
        WHERE spo2 < 87
    );
END$$
DELIMITER ;
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `ViewHospitalData`()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE h_id INT;
    DECLARE h_name VARCHAR(255);
    DECLARE normal_bed INT;
    DECLARE icu_bed INT;
    DECLARE ventilator_bed INT;

    -- Declare a cursor to fetch hospital data
    DECLARE hospital_cursor CURSOR FOR
    SELECT id, hname, normalbed, icubed, vbed
    FROM hospitaldata;

    -- Declare continue handler to exit the loop
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN hospital_cursor;

    -- Start looping through the cursor results
    read_loop: LOOP
        FETCH hospital_cursor INTO h_id, h_name, normal_bed, icu_bed, ventilator_bed;

        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Display the hospital data
        SELECT h_id AS id, h_name AS hname, normal_bed AS normalbed, icu_bed AS icubed, ventilator_bed AS vbed;

    END LOOP;

    CLOSE hospital_cursor;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `GetAllBookingPatients`()
BEGIN
    SELECT * FROM bookingpatient;
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER `Delete` BEFORE DELETE ON `hospitaldata` FOR EACH ROW INSERT INTO status
VALUES(null,OLD.HCODE,OLD.NORMALBED,OLD.ICUBED,OLD.VBED,'DELETED',NOW())
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `Insert` AFTER INSERT ON `hospitaldata` FOR EACH ROW INSERT INTO status
VALUES(null,NEW.HCODE,NEW.NORMALBED,NEW.ICUBED,NEW.VBED,'INSERTED',NOW())
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `Update` AFTER UPDATE ON `hospitaldata` FOR EACH ROW INSERT INTO status
VALUES(null,NEW.HCODE,NEW.NORMALBED,NEW.ICUBED,NEW.VBED,'UPDATED',NOW())
$$
DELIMITER ;

    
