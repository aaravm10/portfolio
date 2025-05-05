/*
 * CSEN 79 Lab: Poker Statistics
 */
#ifndef POKER_H
#define POKER_H

// 5-card Poker
namespace csen79 {
	class Poker {
	public:
		// We play only 5-card poker
		static const int POKER_HANDCARDS = 5;
		enum Rank { 
			POKER_HIGHCARD = 0,
			POKER_PAIR = 1,
			POKER_2_PAIR = 2,
			POKER_TRIPLE = 3,
			POKER_STRAIGHT = 4,
			POKER_FLUSH = 5,
			POKER_FULLHOUSE = 6,
			POKER_QUAD = 7,
			POKER_STRAIGHT_FLUSH = 8,
			POKER_ARRAY_SIZE = 9	// not used
			};
		static const std::string RankNames[POKER_ARRAY_SIZE];

		Poker();
		void dealHand();
		Rank rankHand();
		const Card *getHand(void) const { return hand; }
		friend std::ostream& operator<<(std::ostream& os, const Poker &c);

	private:
		Deck deck;
		// use a member to store the the hand as opposed to dealHand returning a pointer
		// don't want to deal with new/delete yet
		Card hand[POKER_HANDCARDS];

		void sortHand();

		// helper functions for ranking
		bool isFlush(uint s[]);
		bool isStraight(uint r[]);
		bool isQuad(uint r[]);
		bool isTriple(uint r[]);
		bool is2Pair(uint r[]);
		bool isPair(uint r[]);
		bool countRank(uint r[], int);
	};
}

#endif // POKER_H
