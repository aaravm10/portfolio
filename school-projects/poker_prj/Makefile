#
# CSEN 79 Lab: Poker Statistics
#

# This is a Gnu compatible Makefile.  You can read the documentation online by searching Gnu Make
# All coding projects must include a similar Makefile, named "Makefile".  See submission guidelines
STD=-std=c++20
OPT=-g
CXXFLAGS=${STD} ${OPT}
CFLAGS=${OPT}

%.o: %.cxx
	$(CXX) -c $(CXXFLAGS) $<

%: %.cxx
	$(CXX) -o $@ $(CXXFLAGS) $<

DECKSRCS=deckmain.cxx deck.cxx shuffle.cxx card.cxx
DECKOBJS=$(DECKSRCS:.cxx=.o)
CARDSRCS=card.cxx cardmain.cxx
CARDOBJS=$(CARDSRCS:.cxx=.o)
POKERSRCS=poker.cxx pokermain.cxx deck.cxx shuffle.cxx card.cxx
POKEROBJS=$(POKERSRCS:.cxx=.o)
ALL=decktest cardtest pokertest

all: $(ALL)

decktest:	$(DECKOBJS)
	$(CXX) -o $@ $(CXXFLAGS) $+

cardtest:	$(CARDOBJS)
	$(CXX) -o $@ $(CXXFLAGS) $+

pokertest:	$(POKEROBJS)
	$(CXX) -o $@ $(CXXFLAGS) $+

clean:
	/bin/rm -f $(DECKOBJS) $(CARDOBJS) $(POKEROBJS) $(ALL)
	/bin/rm -f poker.tar
	/bin/rm -rf $(ALL:=.dSYM)

depend:
	TMP=`mktemp -p .`; export TMP; \
	sed -e '/^# DEPENDENTS/,$$d' Makefile > $$TMP; \
	echo '# DEPENDENTS' >> $$TMP; \
	$(CXX) -MM  $(DECKSRCS) $(CARDSRCS) $(POKERSRCS) >> $$TMP; \
	/bin/mv -f $$TMP Makefile

tar:
	tar cf poker.tar Makefile *.cxx *.h

# DEPENDENTS
deckmain.o: deckmain.cxx card.h deck.h
deck.o: deck.cxx card.h deck.h
shuffle.o: shuffle.cxx card.h deck.h
card.o: card.cxx card.h
card.o: card.cxx card.h
cardmain.o: cardmain.cxx card.h
poker.o: poker.cxx card.h deck.h poker.h
pokermain.o: pokermain.cxx card.h deck.h poker.h
deck.o: deck.cxx card.h deck.h
shuffle.o: shuffle.cxx card.h deck.h
card.o: card.cxx card.h
