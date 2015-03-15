# Bracket ID isn't unique globally, just by year.
ALTER TABLE `users` DROP INDEX `espn_bracket_id`;
CREATE UNIQUE INDEX `bracket_by_year` ON `users` (`espn_bracket_id`, `year`);

