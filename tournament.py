#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

dbname = 'tournament'

def connect(dbname=dbname):
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect('dbname=' + dbname)

def deleteMatches():
    """Remove all the match records from the database."""
    db = connect(dbname)
    c = db.cursor()
    c.execute("DELETE FROM matches;")
    db.commit()
    db.close()
    return db

def deletePlayers():
    """Remove all the player records from the database."""
    db = connect(dbname)
    c = db.cursor()
    c.execute("DELETE FROM players;")
    db.commit()
    db.close()
    return db

def countPlayers():
    """Returns the number of players currently registered."""
    db = connect()
    c = db.cursor()
    c.execute("SELECT COUNT(id) from players;")
    result = c.fetchall()
    db.close()
    return int(result[0][0])

def registerPlayer(name):
    """Adds a player to the tournament database.
    The database assigns a unique serial id number for the player.

    Args:
      name: the player's full name (need not be unique).
    """
    db = connect()
    c = db.cursor()
    c.execute("INSERT INTO players (name) VALUES (%s)", (name,))
    db.commit()
    db.close()

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    #To order all the players by the number of wins
    query_wins = """select players.id, name, count(matches.id) as wins
                    from players left join matches
                    on players.id = winner_id
                    group by players.id
                    order by wins desc"""

     #To order all the players by the number of losses
    query_losses = """select players.id, name, count(matches.id) as losses
                        from players left join matches
                        on players.id = loser_id
                        group by players.id
                        order by losses desc"""

    query_join = """select winners.id, winners.name, wins, wins+losses as matches
                    from ({query_wins}) as winners left join ({query_losses}) as losers
                    on winners.id = losers.id;""".format(query_wins=query_wins, query_losses=query_losses)

    db = connect()
    c = db.cursor()
    c.execute(query_join + ';')
    results = c.fetchall()

    db.close()
    return results



def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    report_query = """
    INSERT INTO matches (winner_id, loser_id)
    VALUES ({winner_id}, {loser_id})
    """.format(winner_id=winner, loser_id=loser)
    db = connect(dbname)
    c = db.cursor()
    c.execute(report_query)
    db.commit()
    db.close()
    return db

def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = [(record[0], record[1]) for record in playerStandings()]
    left = standings[0::2]
    right = standings[1::2]
    pairings = zip(left, right)

    #To convert back to a tuple
    results = [tuple(list(sum(pairing, ()))) for pairing in pairings]

    return results
