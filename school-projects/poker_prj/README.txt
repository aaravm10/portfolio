Last updated: 6/27/2024

Do these first:
1. rename the directory to "lab2<your ID>".  (No doubel-quotes, <your ID>
is your email without the "@scu.edu" part, or the group name.)

2. type "make" and see everything compile and some executables linked.

3. edit all .h, *.cxx, and Makefile to your ID and email

4. Replace "namespace coen79" to "namespace lab2<your ID>.  Find all the
"using" in every files and do the same.


This is a partial implementation for the lab.  They compile, but does not
work.

Before you start, understand the objectives of the lab.  Write a "test
plan" that ensure thsoe objectives will be met.  You can discuss this with
a partner.

After the successful "make", "cardtest" should be fully working.  Run it to
verify.

Then edit "shuffle.cxx" to implement "shuffle" and "deal" member functions
for class Deck.  After that, make decktest and verify it is indeed working.

Last do poker.  There are two areas: one in poker.cxx and another in
pokermain.cxx.  In a sense, pokermain is testing poker.cxx.  Finish
"RankHand" in poker.cxx.  You probably should write test code (in
pokermain.cxx) just to verify that your RankHand is working.  This is
optional.

Then implement "PokerHands" in pokermain.cxx.  This function is supposed to
find one hand for each poker ranking and print to the screen as it does.
Again, make and verify that.  If this is working, you are in solid ground.
Proceed to do "PokerStats" that collect the statistics for each ranking.

Move all source files to a diretory in one of the school's ECC computer.  Test everything.

