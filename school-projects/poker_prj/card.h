/*
 * CSEN 79 Lab: Poker Statistics
 */
#ifndef CARD_H
#define CARD_H

// short hand to define static const varables

// stand-alone Card class
namespace csen79 {
	class Card {
	public:
	 	/* 
		 * enum is a special "class" that enumerates the possible
		 * names.  Those names are uniquely mapped to intergers that
		 * are contiguous unless overridden In this case, Spade is
		 * "0", and what followed are numerically contiguous
		 */
		enum Suit : int {SPADE=0, HEART, DIAMOND, CLUB};

		/*
		 * "static" means there's only one copy of whatever follows.
		 * Static members exist without needing an instantiated
		 * object.
		 * 
		 * "static const" must be initialized immediately.  "static
		 * const" array must be initialize outside of the class.
		 * 
		 * Rank is the face value of a card.  Together with "suit",
		 * they define a card completely.  Here we chose the legal
		 * range of rank to be [1..13] (inclusive both ends) where
		 * "1" represennt "deuce" and "13" Ace.  Zero is reserved
		 * for error checking
		 * 
		 * It's probably better coding to convert "rank" to enum.
		 * That's just too much typing for me.
		 */
	static const int NRANKS=13; static const int
	HonorIdx = 10; 					// honors' starting here
	static const char Honors[];         // J, Q, K, and Ace
	static const char *suitUCode[];		// unicodes for the suits

	Card(Suit s=SPADE, int r=0): rank{r}, suit{s} {}
	const int getRank() const { return rank; }
	const Suit getSuit() const { return suit; }
	
friend std::ostream& operator<<(std::ostream& os, const Card &c);

// encode a card into an integer
// this facilitate comparison and sorting
	operator int() const { return suit + (rank << 2); }

private:
		int rank;	// A, King, Queen, ..., 2
		Suit suit;
	};
}

#endif // CARD_H
