ALTER TABLE `users` ADD `year` int(4) NOT NULL;

# First year was 2014.
UPDATE `users` SET `year` = 2014;

ALTER TABLE `users` DROP PRIMARY KEY;
ALTER TABLE `users` ADD PRIMARY KEY (`username`, `year`);

