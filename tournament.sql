-- Table definitions for the tournament project.
--
-- To initialize:
-- create db tournament
-- psql tournament


--Table players contains a unique id for each player corresponding to his/her name and time of creation
CREATE TABLE players  ( id serial primary key,
                        name varchar (25) not null,
                        created_at timestamp);

--Table matches contains all match related stats
CREATE TABLE matches  ( id serial primary key,
                        winner_id int,
                        loser_id int,
                        foreign key (winner_id) references players(id),
                        foreign key (loser_id) references players(id) );
