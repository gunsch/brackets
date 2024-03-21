# 2024: ESPN changed their bracket site
ALTER TABLE `users` ADD `espn_new_bracket_id` varchar(36) not null;
CREATE UNIQUE INDEX `new_bracket_by_year` ON `users` (`espn_new_bracket_id`, `year`);
DROP INDEX `bracket_by_year` ON `users`;
