// The MIT License (MIT)
//
// Copyright (c) 2015-2016 Martin Lindhe
// Copyright (c) 2016      Hajime Hoshi
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
// THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
// FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
// DEALINGS IN THE SOFTWARE.

// +build example jsgo



/* 
Modified Version of Game of Life.
The original project is github.com/hajimehoshi/ebiten/tree/master/examples/life

This is not a cellular automaton in a strict case. 
There is a probability for a cell to die at every step that depends 
on the ratio of live cells ratioDelay steps before. 
This delay of ratioDelay steps is introduced to observe a cyclic behavior in population. 

Combination of ratioDelay = (20 to 50) 
and initLiveCellFactor=50 leads to cyclic population.

by DataQubit.

*/

package main

import (
	"log"
	"math/rand"
	"time"
	"github.com/hajimehoshi/ebiten"
	"github.com/hajimehoshi/ebiten/ebitenutil"
	"fmt"
)

// World represents the game state.
type World struct {
	area   []bool
	livecells []float32
	width  int
	height int
}

// NewWorld creates a new world.
func NewWorld(width, height int, maxInitLiveCells int) *World {
	w := &World{
		area:   make([]bool, width*height),
		livecells: make([]float32, ratioDelay), // array that keeps historical live cells ratio
		width:  width,
		height: height,
	}
	w.init(maxInitLiveCells)
	return w
}

func init() {
	rand.Seed(time.Now().UnixNano())
	world = NewWorld(screenWidth, screenHeight, int((screenWidth*screenHeight) / initLiveCellFactor))
}

// init inits world with a random state.
func (w *World) init(maxLiveCells int) {
	for i := 0; i < maxLiveCells; i++ {
		x := rand.Intn(w.width)
		y := rand.Intn(w.height)
		w.area[y*w.width+x] = true
	}
}

// Update game state by one tick.
func (w *World) Update() {
	width := w.width
	height := w.height
	next := make([]bool, width*height)

	cells_ratio := totalLiveCellsRatio(w.area, width, height)
	w.livecells = append(w.livecells, cells_ratio)
	past_cells_ratio := w.livecells[0]
	w.livecells = w.livecells[1:]

	for y := 0; y < height; y++ {
		for x := 0; x < width; x++ {
			if rand.Intn(1000) < int(1000 * past_cells_ratio) {
					// probability that cell will die
					next[y*width+x] = false // w.area[y*width+x]
					//сond_grow := 4
					continue
			}

			pop := neighbourCount(w.area, width, height, x, y)
			switch {
			case pop < 2:
				// rule 1. Any live cell with fewer than two live neighbours
				// dies, as if caused by under-population.
				next[y*width+x] = false

			case (pop == 2 || pop == 3 || pop == 4) && w.area[y*width+x]:
				// modified rule: rule 2. Any live cell with two, three or four live neighbours
				// lives on to the next generation.
				next[y*width+x] = true

			case pop > 4:
				// modified rule: rule 3. Any live cell with more than four live neighbours
				// dies, as if by over-population.
				next[y*width+x] = false

			case pop == 3:
				// rule 4. Any dead cell with exactly three live neighbours
				// becomes a live cell, as if by reproduction.
				next[y*width+x] = true
			}
		}
	}
	w.area = next


}

// Draw paints current game state.
func (w *World) Draw(pix []byte) {
	for i, v := range w.area {
		if v {
			pix[4*i] = 0xff
			pix[4*i+1] = 0x00
			pix[4*i+2] = 0x00
			pix[4*i+3] = 0xff
		} else {
			pix[4*i] = 0
			pix[4*i+1] = 0
			pix[4*i+2] = 0
			pix[4*i+3] = 0
		}
	}
}



// totalLiveCellsRatio computes a ratio of cells 
func totalLiveCellsRatio(a []bool, width, height int) float32 {
	sum := 0
	for _, c := range a {
		if c {
			sum += 1
		}
	}

	return float32(sum) / float32(width * height)
}

// neighbourCount calculates the Moore neighborhood of (x, y).
func neighbourCount(a []bool, width, height, x, y int) int {
	c := 0
	for j := -1; j <= 1; j++ {
		for i := -1; i <= 1; i++ {
			if i == 0 && j == 0 {
				continue
			}
			x2 := x + i
			y2 := y + j
			if x2 < 0 || y2 < 0 || width <= x2 || height <= y2 {
				continue
			}
			if a[y2*width+x2] {
				c++
			}
		}
	}
	return c
}

const (
	screenWidth  = 400
	screenHeight = 400
	ratioDelay = 20
	initLiveCellFactor = 50
)

var (
	world  *World
	pixels = make([]byte, screenWidth*screenHeight*4)
)

func update(screen *ebiten.Image) error {
	world.Update()

	if ebiten.IsDrawingSkipped() {
		return nil
	}

	world.Draw(pixels)
	screen.ReplacePixels(pixels)

	// Display current Live Cell Ratio 
	// and Effective Live Cell Ratio (the ratio that defines the probability of death)
	msg := fmt.Sprintf(`Live Cell Ratio: %0.2f
Effective LCR: %0.2f`, world.livecells[ratioDelay - 1], world.livecells[0])
	ebitenutil.DebugPrint(screen, msg)

	return nil
}

func main() {
	if err := ebiten.Run(update, screenWidth, screenHeight, 2, "Modified Game of Life with Stochastic Elements"); err != nil {
		log.Fatal(err)
	}
}
