from hanabi import *
import util
import agent
import random
        
def format_hint(h):
    if h == HINT_COLOR:
        return "color"
    return "rank"

class SkillIssuePlayer(agent.Agent):
    def __init__(self, name, pnr):
        self.name = name
        self.hints = {}
        self.pnr = pnr
        self.explanation = []

    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints, hits, cards_left):
        for player,hand in enumerate(hands):
            for card_index,_ in enumerate(hand):
                if (player,card_index) not in self.hints:
                    self.hints[(player,card_index)] = set()
        known = [""]*5
        for h in self.hints:
            pnr, card_index = h 
            if pnr != nr:
                known[card_index] = str(list(map(format_hint, self.hints[h])))
        self.explanation = [["hints received:"] + known]

        my_knowledge = knowledge[nr]
        
        potential_discards = []
        for i,k in enumerate(my_knowledge):
            if util.is_playable(k, board):
                return Action(PLAY, card_index=i)

            #if util.maybe_playable(k, board):
            #    if (util.probability(util.playable(board), k) >= 0 and hits < 2):
            #        return Action(PLAY, card_index=i)

            if util.is_useless(k, board):    
                potential_discards.append(i)
                
        if potential_discards:
            return Action(DISCARD, card_index=random.choice(potential_discards))
         
        playables = []        
        for player,hand in enumerate(hands):
            if player != nr:
                for card_index,card in enumerate(hand):
                    if card.is_playable(board):                              
                        playables.append((player,card_index))
        
        playables.sort(key=lambda which: -hands[which[0]][which[1]].rank)
        while playables and hints > 0:
            player,card_index = playables[0]
            knows_rank = True
            real_color = hands[player][card_index].color
            real_rank = hands[player][card_index].rank
            k = knowledge[player][card_index]
            
            hinttype = [HINT_COLOR, HINT_RANK]
            
            
            for h in self.hints[(player,card_index)]:
                hinttype.remove(h)
            
            t = None
            if hinttype:
                t = random.choice(hinttype)
            
            if t == HINT_RANK:
                for i,card in enumerate(hands[player]):
                    if card.rank == hands[player][card_index].rank:
                        self.hints[(player,i)].add(HINT_RANK)
                return Action(HINT_RANK, player=player, rank=hands[player][card_index].rank)
            if t == HINT_COLOR:
                for i,card in enumerate(hands[player]):
                    if card.color == hands[player][card_index].color:
                        self.hints[(player,i)].add(HINT_COLOR)
                return Action(HINT_COLOR, player=player, color=hands[player][card_index].color)
            
            playables = playables[1:]
 
        if hints > 0:
            hints = util.filter_actions(HINT_COLOR, valid_actions) + util.filter_actions(HINT_RANK, valid_actions)
            
            #this will give one of the hints inside the list of possible things to hint.
            
            hintgiven = random.choice(hints)

            if hintgiven.type == HINT_COLOR:
                for i,card in enumerate(hands[hintgiven.player]):
                    if card.color == hintgiven.color:
                        self.hints[(hintgiven.player,i)].add(HINT_COLOR)
            else:
                for i,card in enumerate(hands[hintgiven.player]):
                    if card.rank == hintgiven.rank:
                        self.hints[(hintgiven.player,i)].add(HINT_RANK)
                
            return hintgiven

        


        #for i,k in enumerate(my_knowledge):
        #    print(k)
        
        
        #print(board)

        

        #if it could be a value that's useful, it goes into num
        nums = [0, 0, 0, 0, 0]
        #if it could be a value, it goes into denom
        denoms = [0, 0, 0, 0, 0]


        #For each card:
        cardIndex = 0
        for i in my_knowledge:
            
            #print(my_knowledge[cardIndex])
            #print(cardIndex)
            #for the colors in the card:
            colorIndex = 0
            for j in i: 
                #print(my_knowledge[cardIndex][colorIndex])
                cardOnBoard = board[colorIndex][1]
                
                #print(cardOnBoard)
                
                
                for k in j:
                    denoms[cardIndex] = denoms[cardIndex] + k
                    if cardOnBoard < k:
                        nums[cardIndex] = nums[cardIndex] + k
                #print("num is: ")
                #print(nums)
                #print("denom is ")
                #print(denoms)
                colorIndex = colorIndex + 1
                    
            cardIndex = cardIndex + 1
        
        #print("num is: ")
        #print(nums)
        #print("denom is ")
        #print(denoms)
        totals = [0.0, 0.0, 0.0, 0.0, 0.0]

        #doing it like this because idk why python wouldn't accept the other way
        i = 0
        for total in totals:
            totals[i] = totals[i] + nums[i] / denoms[i]

            i = i + 1
                
        #print(totals)

        index = 0
        i = 0
        max = 50
        for denom in denoms:
            if max <= denom:
                index = i
                max = denom
            i = i + 1
        #print(max)
        #print(index)

        possibleDiscards = util.filter_actions(DISCARD, valid_actions)

        return possibleDiscards[index]


            

                    
                    

        

    def inform(self, action, player):
        if action.type in [PLAY, DISCARD]:
            if (player,action.card_index) in self.hints:
                self.hints[(player,action.card_index)] = set()
            for i in range(5):
                if (player,action.card_index+i+1) in self.hints:
                    self.hints[(player,action.card_index+i)] = self.hints[(player,action.card_index+i+1)]
                    self.hints[(player,action.card_index+i+1)] = set()

    

agent.register("skill", "Skill Issue Player", SkillIssuePlayer)
