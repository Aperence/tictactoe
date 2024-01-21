Example of application using channels for game networks
```
cd server && mix phx.server

# first player with X
python3 game.py X 

# second player with O
python3 game.py O

# Third player is only an observer of the game
python3 game.py V
```