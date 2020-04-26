import random

class _2x2:
    _u = ((0, 1, 2, 3), (4, 8, 12, 16), (5, 9, 13, 17))
    _f = ((4, 5, 6, 7), (2, 11, 20, 17), (3, 8, 21, 18))
    _r = ((8, 9, 10, 11), (1, 15, 21, 5), (2, 12, 22, 6))
    def __init__(self):
        self._modle = tuple(range(24))

    # def U(self):
        # self._modle = self._perm(*self._u)
    
    # def U_(self):
        # self._modle = self._perm(*self._u, inverse = True)
    
    # def U2(self):
        # self._modle = self._perm(*self._u)
        # self._modle = self._perm(*self._u)

    # def F(self):
        # self._modle = self._perm(*self._f)
    
    # def F_(self):
        # self._modle = self._perm(*self._f, inverse = True)
    
    # def F2(self):
        # self._modle = self._perm(*self._f)
        # self._modle = self._perm(*self._f)
        
    # def R(self):
        # self._modle = self._perm(*self._r)
    
    # def R_(self):
        # self._modle = self._perm(*self._r, inverse = True)
    
    # def R2(self):
        # self._modle = self._perm(*self._r)
        # self._modle = self._perm(*self._r)
    
    @classmethod
    def _perm(cls, puzzle, *perms, inverse = False):
        res = [e for e in puzzle._modle]
        for perm in perms:
            perm = tuple(reversed(perm)) if inverse else perm
            for c, n in zip(perm, perm[1:]+(perm[0],)):
                res[n] = puzzle._modle[c]
        return res
    
    def solve(self, target = tuple(range(24)), moves = ()):
        diff = lambda state, target: sum(abs(c-t) for c, t in zip(state, target))
        state_diff = diff(self._modle, target)
        if state_diff == 0:
            return moves
        state = self._modle
        for perm, inverse in [(self._u, True), (self._u, False),
                              (self._f, True), (self._f, False),
                              (self._r, True), (self._r, False)]:
            new_state = self._perm(self, *perm, inverse = inverse)
            new_state_diff = diff(new_state, target)
            if new_state_diff < state_diff:
                self._modle = new_state
                print('\t'*len(moves) + str(perm))
                solve_ = self.solve(target, moves + (perm,))
                self._modle = state
                if type(solve_) != str:
                    return solve_
        return f'Bad State: {state} or Targe: {target}'
