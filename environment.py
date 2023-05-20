from collections import *
import random

raw_cards = ['01피', '01피', '01홍단', '01광', '02피', '02피', '02고도리멍', '02홍단', '03피', '03피', '03홍단', '03광',
                '04피', '04피', '04고도리멍', '04초단', '05피', '05피', '05초단', '05멍', '06피', '06피', '06청단', '06멍',
                '07피', '07피', '07초단', '07멍', '08피', '08피', '08고도리멍', '08광', '09피', '09피', '09국진멍', '09청단',
                '10피', '10피', '10청단', '10멍', '11피', '11피', '11쌍피', '11광', '12쌍피', '12멍', '12단', '12비광']

class Card():
    def __init__(self, name, month, type, feature):
        self.name = name
        self.month = month
        self.type = type
        self.feature = feature
    def __repr__(self):
        return self.name

cards = [Card(c ,int(c[:2]), c[-1], c[2:-1] if c[2:-1] else None) for c in raw_cards]
bonus = Card('보너스', '', '피', '쌍')
cards += [bonus, bonus]
for c in cards: c.name = f'{c.month}{c.feature}' if c.feature is not None else f'{c.month}{c.type}'
cards_by_name = {c.name: c for c in cards}
START_MONEY = 10000

def return_names(cards):
    return [c.name for c in cards]

def return_cards(names):
    return [cards_by_name[n] for n in names]

def filter_cards(condition, cards):
    return list(filter(condition, cards))

def move_card(start, end, card):
    start.remove(card)
    end.append(card)
    return None

class Player():
    def __init__(self, name, is_human):
        self.name = name
        self.is_human = is_human
        self.matched = {'피':[], '멍':[], '단':[], '광':[]}
        self.hand = []
        self.money = START_MONEY
        self.fucked = []
    
    def decide_hit(self, ground):    
        if self.is_human:
            while True:
                hit = input(f'{self.hand}에서 칠 카드를 입력하세요 :')
                hit = filter_cards(lambda c: c.name == hit, self.hand)
                if hit: 
                    hit = hit[0]
                    break
        elif not self.is_human:
            pass #ai가 들어갈 부분    
        return hit

    def memorize_fuck(self, month):
        self.fucked.append(month)
        return None
        
            

class Game():
    def __init__(self, player1, player2, player3, cards):
        self.player1 = player1
        self.player2 = player2
        self.player3 = player3
        self.cards = cards
        self.ground = []
        self.deck = []
        self.order = [self.player1, self.player2, self.player3]
    
    def shuffle(self):
        random.shuffle(self.cards)
        self.player1.hand = self.cards[:7]
        self.player2.hand = self.cards[7:14]
        self.player3.hand = self.cards[14:21]
        self.ground = self.cards[21:27]
        self.deck = self.cards[27:]
        return None
    
    def set_order(self, winner_name):
        if winner_name == self.player1.name: self.order = [self.player1, self.player2, self.player3]
        elif winner_name == self.player2.name: self.order = [self.player2, self.player3, self.player1]
        elif winner_name == self.player3.name: self.order = [self.player3, self.player1, self.player2]
        return None
    
    def get_others(self, player):
        others = self.order[:]
        others.remove(player)
        return others
    
    def add_to_matched(self, start, player, card):
        if card.feature == '국진':
            while True:
                decided_type = input('\'멍\'과 \'피\' 중에서 국진을 놓을 곳을 입력하세요 : ')
                if decided_type in ['멍', '피']:
                    move_card(start, player.matched[decided_type], card)
                    return None
        move_card(start, player.matched[card.type], card)
        return None
    
    def hit_to_ground(self, player, card):
        move_card(player.hand, self.ground, card)
        return None
    
    def choose_on_ground(self, player, candidates):
        if not candidates: return
        if player.is_human:
                while True:
                    chosen = input(f'{candidates}에서 가져갈 카드를 입력하세요 :')
                    chosen = filter_cards(lambda c: c.name == chosen, candidates)
                    if chosen: 
                        chosen = chosen[0]
                        break
        elif not self.is_human:
            pass #ai가 들어갈 부분
        return chosen

    def rob_matched_from_others(self, player, rob_count):
        others = self.get_others(player)
        for other in others:
            robbed = []
            double = filter_cards(lambda c: c.feature in ['쌍', '국진'], other.matched['피'])
            single = filter_cards(lambda c: c.feature is None, other.matched['피'])
            if len(single) + 2*len(double) <= rob_count:
                robbed = other.matched['피'][:]
            elif len(single) <= rob_count:
                rob_double_count = (rob_count - len(single) + 1) // 2
                robbed += random.sample(double, rob_double_count)
                robbed += random.sample(single, max([rob_count - 2*rob_double_count,0]))
            elif len(single) > rob_count:
                robbed += random.sample(single, rob_count)    
            
            for card in robbed: self.add_to_matched(other.matched['피'], player, card)
        return None
            
    def calculate_pea(self, player):
        double = filter_cards(lambda c: c.feature in ['쌍', '국진'], player.matched['피'])
        return len(player.matched['피']) + len(double)
    
    def hit_and_draw(self, player):
        rob_count = 0
        temporarily_matched = []
        have_to_choose = False
        candidates_for_hit = []
        candidates_for_drawn = []
        
        while True:
            hit = player.decide_hit(self.ground)
            if hit.name != '보너스': break
            elif hit.name == '보너스':
                self.add_to_matched(player.hand, player, hit)
        
        able_on_ground = filter_cards(lambda c: c.month == hit.month, self.ground)
        self.hit_to_ground(player, hit)
        
        if len(able_on_ground) == 3: 
            for target in able_on_ground:
                temporarily_matched.append(target)
            temporarily_matched.append(hit)
            rob_count += 1
            if target.month in player.fucked: rob_count += 1
                    
        elif len(able_on_ground) == 2: 
            have_to_choose = True
            candidates_for_hit = able_on_ground[:]
            temporarily_matched.append(hit)
            
        elif len(able_on_ground) == 1:
            matched_with_hit = able_on_ground.pop()
            temporarily_matched.append(matched_with_hit)
            temporarily_matched.append(hit)
        
        elif len(able_on_ground) == 0: pass
        
        while True:
            drawn = self.deck[0]
            if drawn.name != '보너스': break
            elif drawn.name == '보너스':
                self.add_to_matched(self.deck, player, drawn)
        
        able_on_ground = filter_cards(lambda c: c.month == drawn.month, self.ground)
        move_card(self.deck, self.ground, drawn)
        
        if len(able_on_ground) == 3: 
            if hit in able_on_ground: #따닥
                have_to_choose = False
                temporarily_matched += candidates_for_hit
                rob_count += 1
            
            elif hit not in able_on_ground:    
                for target in able_on_ground:
                    temporarily_matched.append(target)
                temporarily_matched.append(drawn)
                rob_count += 1
                if target.month in player.fucked: rob_count += 1
                        
        elif len(able_on_ground) == 2:
            if hit in able_on_ground: #뻑
                temporarily_matched = []
                player.memorize_fuck(hit.month)
                
            elif hit not in able_on_ground:    
                have_to_choose = True
                candidates_for_drawn = able_on_ground[:]
                temporarily_matched.append(drawn)    
                
        elif len(able_on_ground) == 1:
            if hit in able_on_ground: #쪽
                temporarily_matched.append(hit)
                temporarily_matched.append(drawn)
                rob_count += 1
            
            elif hit not in able_on_ground:    
                target = able_on_ground.pop()
                temporarily_matched.append(target)
                temporarily_matched.append(drawn)
        
        elif len(able_on_ground) == 0: pass
        
        if have_to_choose:
            if candidates_for_hit:
                temporarily_matched.append(self.choose_on_ground(player, candidates_for_hit))
            if candidates_for_drawn:
                temporarily_matched.append(self.choose_on_ground(player, candidates_for_drawn))
        
        for card in temporarily_matched:
            self.add_to_matched(self.ground, player, card)
        
        if not self.ground: #쓸
            rob_count += 1 
        
        self.rob_matched_from_others(player, rob_count)
    
    def print_state(self):
        print(f'{self.player1.name}\n'
                f'hand: {self.player1.hand}\n'
                f'matched: {self.player1.matched}\n'
                f'{self.player2.name}\n'
                f'hand: {self.player2.hand}\n'
                f'matched: {self.player2.matched}\n'
                f'{self.player3.name}\n'
                f'hand: {self.player3.hand}\n'
                f'matched: {self.player3.matched}\n'
                f'ground:{self.ground}\n'
                f'deck:{self.deck}')
    
    def custom_game(self):
        self.player1.hand = return_cards(['1피'])
        self.player2.hand = return_cards(['8피'])
        self.player3.hand = []
        self.player1.matched['피'] = return_cards([])
        self.player2.matched['피'] = return_cards(['보너스', '12쌍'])
        self.player3.matched['피'] = return_cards(['11쌍', '10피', '5피', '9피'])
        self.ground = return_cards(['1광', '1피', '1홍', '2피', '2고도리', '2홍'])
        self.deck = return_cards(['2고도리', '8고도리'])
        return None

if __name__ == '__main__':
    p1 = Player('me', True)
    p2 = Player('opp1', True)
    p3 = Player('opp2', True)
    game = Game(p1, p2, p3, cards)
    game.custom_game()
    game.print_state()
    game.hit_and_draw(game.player1)
    game.print_state()      
