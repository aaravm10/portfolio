/*
 * Name: Aarav Mehta
 * Email: ahmehta@scu.edu
 */
#include <iostream>
#include "card.h"
#include "deck.h"
#include <cstdlib>
#include <time.h> 


namespace csen79 {
	// implement Fisher-Yates here
	void Deck::shuffle(void) {
		srand (time(NULL)); 
		
		for(int i = CARDS_PER_DECK - 1; i > 0; i--){
			int j = rand() % (i + 1);
			std::swap(cards[i],cards[j]);
		}
		next = 0;
	}

	// deal out one card
	const Card &Deck::deal() {
		if (next >= CARDS_PER_DECK - guard){
			shuffle();
		}
		return  cards[next++];	// replace this line with your implementation of the function.
	}
}

