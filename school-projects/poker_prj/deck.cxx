/*
 * CSEN 79 Lab: Poker Statistics
 */
#include <iomanip>
#include <iostream>
#include <cstdlib>
#include <time.h>

using namespace std;
#include "card.h"
#include "deck.h"

// Deck class implementation
namespace csen79 {
	// workhorse constructor
	Deck::Deck(int g): next(0), guard(g) {
		nCards = Deck::CARDS_PER_DECK;
		int i = 0;
		for (auto s = Card::Suit::SPADE; s <= Card::Suit::CLUB; s=static_cast<Card::Suit>(s+1)) {
			for (auto r = 1; r <= Card::NRANKS; r++)
				cards[i++] = Card(s, r);
		}

		// for shuffling.  Change to a constant for debugging
		srand(time(0));
	}

	// print 13 cards each row
	ostream& operator<<(ostream& os, const Deck &d) {
		int i = 0;
		while (i < d.nCards) {
			int row = 13;
			while (row-- > 0) {
				cout << d.cards[i];
				i++;
			}
			cout << endl;
		}
		return os;
	}
}

