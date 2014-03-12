CREATE TABLE `users` (
    `username` varchar(255) primary key,
    `subreddit` varchar(255) not null,
    `espn_bracket_id` int(10) not null);
