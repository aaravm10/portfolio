/*
 * CSEN 79 Lab: Poker Statistics
 */
#include <ctime>
#include <iomanip>
#include <iostream>
#include <cstring>
#include <cmath>
#include "card.h"
#include "deck.h"
#include "poker.h"


using namespace std;
using namespace csen79;


int rank_arr[9] = {Poker::POKER_HIGHCARD,
		   Poker::POKER_PAIR,
		   Poker::POKER_2_PAIR,
		   Poker::POKER_TRIPLE, 
		   Poker::POKER_STRAIGHT, 
		   Poker::POKER_FLUSH, 
		   Poker::POKER_FULLHOUSE, 
		   Poker::POKER_QUAD, 
		   Poker::POKER_STRAIGHT_FLUSH};


string rank_string[9] = {"High Card" , "Pair", "Two Pairs", "Triple", "Straight", "Flush", "Full House", "Four of a Kind", "Straight Flush"}; 

// Generate one sample hand for each rank
void pokerHands(Poker &poker) {
	/*
	 * Loop until you have found one of each rank.
	 * Print that "sample hand"
	 */
		
	int flag = 0;
	while (flag != 0x1ff){
		int rank;
		poker.dealHand();
		rank = poker.rankHand();
		
		for(int i = 0; i < 9; i++){
			if((flag & (1 << rank_arr[i])) == 0){
				if(rank == rank_arr[i]){
					cout << setw(14) << rank_string[i] << ": " << poker << endl;
					flag |= 1 << rank_arr[i];
				}
			}
		}
	}	 

}

// Collect statistics for each rank of Poker
void pokerStats(Poker &poker) {
	int count;
	cout << endl;
	cout << "Enter number of iterations to run: ";
	cin >> count;
	cout << endl;
	
	int hand_count[9] = {0}; 
	
	time_t tmark = clock();			// ready, get set, go!
	/*
	 * Do your thing here.
	 * This is supposed to be big loop that deal many many poker hands and collect the
	 * statistics for each rank.
	 * Once you believe the statistics are good.  Exit the loop.
	 * "tmark" then computes the number of "clock ticks" in your loop.
	 * You should convert that to human friendly units, such as "seconds"
	 * 
	 * Output your stats then, with the amount of time it took you collect the stats.
	 */	
	for(int i = 0; i < count; i++){
		int rank;
		poker.dealHand();
		rank = poker.rankHand();
		hand_count[rank]++;
	}
	
	tmark = clock() - tmark;	// stop the clock
	
	double avg = (((double)tmark/CLOCKS_PER_SEC) / count) * 50000;
	
	cout << "Dealt " << count << " hands. Elapsed time: " << ((double)tmark/CLOCKS_PER_SEC) << " seconds." << endl;
	cout << "Average: " << avg << " seconds per 50k hands" << endl;
	
	for(int i = 8; i >= 0; i--){
		double percentage = ((double)(hand_count[i]) * 100) / count;
		cout << fixed << setprecision(2);
		cout << setw(14) << rank_string[i] << ": " << setw(10) << hand_count[i] << " " << percentage << "%" << endl;
	}	
}

int main(void) {
	Poker poker;
	cout << "Sample hand for each Rank:" << endl;
	pokerHands(poker);
	cout << endl << "Statistics:" << endl;
	pokerStats(poker);

	return EXIT_SUCCESS;
}
