* Modified Version of Game of Life in Golang. 

The original project is github.com/hajimehoshi/ebiten/tree/master/examples/life

This is not a cellular automaton in a strict sense. 
There is a probability for a cell to die at every step that depends 
on the ratio of live cells ratioDelay steps before. 
This delay of ratioDelay steps is introduced to observe a cyclic behavior in population. 

Combination of ratioDelay = (20 to 50) 
and initLiveCellFactor=50 leads to cyclic population.

To me it's just a fun project to practice Go.
