Example of application using channels/websockets for game backend 
```
cd server && mix phx.server

cd frontend

# first player with X, in room 42
python3 game.py X 42

# second player with O, in room 42
python3 game.py O 42

# Third player is only an observer of the game, still in room 42
python3 game.py V 42
```