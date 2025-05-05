/*
 * Name: Aarav Mehta
 * Email: ahmehta@scu.edu
 */
#include <iomanip>
#include <iostream>
#include "card.h"

using namespace std;
using namespace csen79;

// Test program for Card
int main(void) {
	cout << "Card Testing" << endl;
	for (auto s = Card::Suit::SPADE; s <= Card::Suit::CLUB; s=static_cast<Card::Suit>(s+1)) {
		for (auto r = 1; r <= Card::NRANKS; r++) 
			cout << Card(s, r);
		cout << endl;
	}
}
