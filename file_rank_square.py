# /usr/bin/python

# Used by App and BoardView
class BoardCoords(object):
    def __init__(self, file_, rank):
        self.file = file_
        self.rank = rank

# Used by App and Chess Model
# file and rank inds to square name (e.g. "a1")
def file_rank2square_name(file_, rank):
    return chr(ord('a')+file_) + chr(ord('1')+rank)

# Used by App only, but keep with above
# square name (e.g. "a1") to file and rank inds
def square_name2file_rank(square_name):
    file_ = ord(square_name[0]) - ord('a')
    rank = ord(square_name[1]) - ord('1')
    return BoardCoords(file_, rank)
