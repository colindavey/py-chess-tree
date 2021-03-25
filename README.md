# py-chess-tree

In this repo, I have continued the work from my 2016 python two-week challenge that you can find here: [https://github.com/colindavey/py-chess-tree-two-week-challenge] -- an opening repertoire editor for chess because there was no existing program that let me edit chess openings the way I wanted to, by viewing and editing the repertoire's tree structure.

In this version, I have been mostly refactoring, improving the overall structure and style of the code, as well as, more recently, improving the features. The main goal of the refactoring is to shape the GUI portion so that it can be a model for how to implement it as a web application in React, with part of the python code moved to a REST API endpoint that the React app can use. 

My work on the React side can be found here: [https://github.com/colindavey/react-tic-tac-toe-to-chess]. It's called react-tic-tac-toe-to-chess because I started with the code from the React tic-tac-toe tutorial, and gradually warped it until it was a chess app. 
