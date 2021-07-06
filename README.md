# Always Winning in Mancala

This program allows you to win any mancala game as long as your opponent doesn't
notice you looking back and forth at your laptop.

## How to Cheat

By default, the script assumes a standard game of mancala with 6 "holes" on each
side of the board and 4 beans in each hole. It also assumes that the human
player goes first (because otherwise the AI will win in one turn). There are
commandline flags to modify these defaults which you can see by running:
```
$ python3 mancala.py -h
```

To give a run down of the flags...
- `--num_tiles_per_player`: This changes how many holes each player has on their
side. I think 6 is pretty standard but in case you want to change that, there
you go.
- `--num_beans_per_tile`: This changes how many "beans" are in each hole. Again,
4 feels pretty standard but the knob to change it is there if needed.
- `--ai_first`: If you enable this flag, AI player will go first and with enough
lookaheads, it'll almost always win in one move. Use it sparingly.
- `--num_lookahead`: This changes how many "turns" the AI player will simulate.
The default of 5 already takes quite a bit to chug through so be careful with
this one too.

### A Real Life Example

Say you're playing a friendly game of Mancala with your girlfriend's mother and
she seems to be owning you every time. You say "hey, you're very good. Let me go
get my laptop real quick." You go get your laptop and you load up your favorite
terminal. You run the following command:
```
$ python3 mancala.py --ai_first
```
The script will spit out the following:
```
Starting game...
Initial board state:
(0) 4 4 4 4 4 4 
 4 4 4 4 4 4 (0)
Generating new tree, please wait...
Finished generating tree
Smart Player is doing this move: Player index: 0, Tile index: 5
Player 0 can go again!
Smart Player is doing this move: Player index: 0, Tile index: 5
Player 0 can go again!
Smart Player is doing this move: Player index: 0, Tile index: 2
...
```
All you need to do is look for `Smart Player is doing this move:...` and copy it
perfectly IRL. So in the example above, your first 3 moves are:
1. On your side, choose the 5th index hole and start distributing the beans
2. Again on your side, choose the 5th index hole and start distributing the beans
3. Again on your side, choose the 2nd index hole and start distributing the beans

If you let your opponent go first, you'll see:
```
$ python3 mancala.py 
Starting game...
Initial board state:
(0) 4 4 4 4 4 4 
 4 4 4 4 4 4 (0)
Type in your move:
```
You just need to type the index of the hole that they picked up and the script
will simulate what should've happened IRL. If they get to go again, type in
their index again and so on until the AI picks its moves.