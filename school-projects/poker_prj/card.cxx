/*
 * CSEN 79 Lab: Poker Statistics
 */
#include <iomanip>
#include <iostream>
#include "card.h"
using namespace std;

// Stand-alone Card definitions
namespace csen79 {

	// initialize static const arrays
	const char Card::Honors[] = {'J', 'Q','K', 'A'};
	const char *Card::suitUCode[] = {"\u2660", "\u2665", "\u2666", "\u2663"};

	// formatted output
	ostream& operator<<(ostream& os, const Card &c) {
		// Reserving 0/0 for invalid card
		if (c.rank == 0)
			os << "Not a Card";
		else {
			// Fancy way to display unicode suit glyphs
			// That's Spade, Heart, Diamond, and Club
			os << c.suitUCode[c.suit];
			// Note Ace is the high card, numerically 14
			// Deuce is low, numerically 2
			if (c.rank >= c.HonorIdx ) {
				os << c.Honors[c.rank - c.HonorIdx];
			} else
				os << c.rank+1;
		}
		return os;
	}
}
