/*
 * CSEN 79 Lab: Poker Statistics
 */
namespace csen79 {
	/*
	 * Abstract one deck of playing cards, without Jokers.
	 * "deal" function return the top of the deck.  It resuffles if
	 * the deck has reached below the "guard" value.
	 */
	class Deck {
	public:
		static const size_t CARDS_PER_DECK = 52;
		Deck(): Deck(5) {}	// default guard
		Deck(int);	// argument is the guard
		const Card &deal(void);
		void shuffle(void);

	friend std::ostream& operator<<(std::ostream& os, const Deck &);

	private:
		int nCards;	// for future versions that has multiple decks
		Card cards[CARDS_PER_DECK];
		int next;
		int guard;
	};
}
