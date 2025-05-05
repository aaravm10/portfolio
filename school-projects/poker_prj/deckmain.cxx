/*
 * CSEN 79 Lab: Poker Statistics
 */
#include <iomanip>
#include <iostream>
#include "card.h"
#include "deck.h"

using namespace std;
using namespace csen79;


// Test program for Deck class
int main(void) {
	Deck deck;
	cout << "Fresh deck: " << endl << deck << endl;
	deck.shuffle();
	int nDeals{20};
	cout << "Shuffle then deal " << nDeals * 13 << " cards" << endl;
	int stats[Deck::CARDS_PER_DECK] = {0};
	// Essentially test only with dealing.  That trigger shuffling
	for (auto i = 0; i < nDeals; i++) {
		cout << setw(2) << i + 1 << setw(0) << ": ";
		for (auto j = 0; j < 13; j++) {
			Card c = deck.deal();
			cout << c;
			stats[c-4]++;
		}
		cout << endl;
	}

	return 0;
}

