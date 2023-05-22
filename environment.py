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
bonus = Card('보너스', '', '피', '보너스')
cards += [bonus, bonus]
for c in cards: c.name = f'{c.month}{c.feature}' if c.feature is not None else f'{c.month}{c.type}'
cards_by_name = {c.name: c for c in cards}
START_MONEY = 10000
MONEY_PER_SCORE = 100
FIRST_FUCK = 500
THREE_FUCK = 700
LAST_TURN = 6
TOTAL_GAME = 1
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
        self.score = 0
        self.lastscore = 0
        self.fucked = []
        self.stop = False
        self.go = 0
        self.score_addition = 0
        self.score_multiplication = 1
        self.bak = 1
    
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
    
    def count_pea(self): 
        double = filter_cards(lambda c: c.feature in ['쌍', '국진', '보너스'], self.matched['피'])
        return len(self.matched['피']) + len(double) - 9

    def calculate_pea_score(self):
        return max([0, self.count_pea()-9])
    
    def is_peabak(self):
        if self.count_pea() in range(1,6): 
            self.bak *= 2
            return True
        return False
    
    def count_mung(self):
        return len(self.matched['멍'])
    
    def is_godori(self):
        godori = filter_cards(lambda c: c.feature == '고도리', self.matched['멍'])
        return len(godori) == 3
    
    def calculate_mung_score(self):
        mung_count = self.count_mung()
        if mung_count >= 7: self.score_multiplication *= 2
        return self.is_godori() * 5 + max([0, mung_count - 4])
    
    def count_dan(self):
        return len(self.matched['단'])
    
    def count_set_of_dan(self):
        chung = filter_cards(lambda c: c.feature == '청', self.matched['단'])
        hong = filter_cards(lambda c: c.feature == '홍', self.matched['단'])
        cho = filter_cards(lambda c: c.feature == '초', self.matched['단'])
        return sum(filter(lambda count: count == 3, [chung, hong, cho]))

    def calculate_dan_score(self):
        return self.count_set_of_dan() * 3 + max([0, self.count_dan() - 4])

    def count_gwang(self):
        return len(self.matched['광'])
    
    def include_bea(self):
        bea = filter_cards(lambda c: c.feature == '비', self.matched['광'])
        return len(bea)
    
    def calculate_gwang_score(self):
        gwang_count = self.count_gwang()
        if gwang_count <= 2: return 0
        elif gwang_count == 3:
            if self.include_bea(): return 2
            return 3
        elif gwang_count == 4: return 4
        return 15
    
    def is_gwangbak(self):
        if not self.count_gwang():
            self.bak *= 2
            return True
        return False 
    
    def calculate_score(self):
        self.score = sum([self.calculate_pea_score(), 
                        self.calculate_mung_score(), 
                        self.calculate_dan_score(), 
                        self.calculate_gwang_score()])
    
    def _decide_to_stop(self):
        if self.is_human:
            while True:
                decision = input(f'\'고\' or \'스톱\'? ')
                if decision in ['고', '스톱']:
                    break
        elif not self.is_human:
            decision = '스톱' #ai가 들어갈 부분
        return decision == '스톱'
        
    
    def go_or_stop(self):
        if self.go:
            if self.score > self.lastscore:
                stop = self._decide_to_stop()
                if stop: self.stop = True
                elif not stop: 
                    self.go += 1
                    if self.go == 2: self.score_addition = 2
                    elif self.go >= 3: self.score_multiplication *= 2
        elif self.score >= 3:
                stop = self._decide_to_stop()
                if stop: self.stop = True
                elif not stop: 
                    self.go += 1
                    self.score_addition = 1
        return None


class Game():
    def __init__(self, player1, player2, player3, cards):
        self.game_number = 1
        self.player1 = player1
        self.player2 = player2
        self.player3 = player3
        self.cards = cards
        self.ground = []
        self.deck = []
        self.order = [self.player1, self.player2, self.player3]
        self.winner = random.choice(self.order)
        self.nagari = 0
        self.draw = False
        self.three_fuck = False
    
    def shuffle(self):
        random.shuffle(self.cards)
        self.player1.hand = self.cards[:7]
        self.player2.hand = self.cards[7:14]
        self.player3.hand = self.cards[14:21]
        self.ground = self.cards[21:27]
        self.deck = self.cards[27:]
        while self.ground.count(return_cards(['보너스'])[0]):
            self.add_to_matched(self.ground, self.winner, return_cards(['보너스'])[0])
            move_card(self.deck, self.ground, self.deck[0])
        return None
    
    def set_order(self):
        winner_name = self.winner.name
        if winner_name == self.player1.name: self.order = [self.player1, self.player2, self.player3]
        elif winner_name == self.player2.name: self.order = [self.player2, self.player3, self.player1]
        elif winner_name == self.player3.name: self.order = [self.player3, self.player1, self.player2]
        return None

    def reset(self): ##나중에 한번에 정리
        self.ground = []
        self.deck = []
        self.draw = False
        self.three_fuck = False
        for player in self.order:
            player.matched = {'피':[], '멍':[], '단':[], '광':[]}
            player.hand = []
            player.fucked = []
            player.score = 0
            player.lastscore = 0
            player.stop = False
            player.go = 0
            player.score_addition = 0
            player.score_multiplication = 2 ** self.nagari
            player.bak = 1
        return None
    
    def play_game(self):
        self.shuffle()
        turns = range(LAST_TURN + 1)
        for turn in turns:
            for player in self.order:
                self.print_state()
                self.hit_and_draw(player, turn)
                if not self.three_fuck: 
                    player.calculate_score()
                    player.go_or_stop()
                    if player.stop:
                        self.winner = player
                        return None
                elif self.three_fuck:
                    self.winner = player
                    return None
        self.draw = True

    def get_money_from_others(self):
        if self.draw:
            self.nagari += 1
            return None    
        winner = self.winner
        losers = self.get_others(winner)
        win = 0
        scored_by_pea = winner.calculate_pea_score()
        scored_by_gwang = winner.calculate_gwang_score()
        winner.score_multiplication = 2 ** self.nagari
        if self.three_fuck:
            winner.money += 2*THREE_FUCK
            for loser in self.get_others(winner):
                loser.money -= THREE_FUCK
            return None
        for loser in losers:
            if scored_by_pea: loser.bak *= 2 ** loser.is_peabak #피박
            if scored_by_gwang: loser.bak *= 2 ** loser.is_gwangbak #광박
            if loser.go: loser.bak *= 2 #고박
            lose = (winner.score + winner.score_addition) * winner.score_multiplication * loser.bak
            loser.money -= lose
            win += lose
        winner.money += win
        return None
    
    def play(self):
        while self.game_number <= TOTAL_GAME:
            self.set_order()
            self.reset()
            self.play_game()
            self.get_money_from_others()
            self.game_number += 1
        return None

    
    def get_others(self, player):
        others = self.order[:]
        others.remove(player)
        return others
    
    def add_to_matched(self, start, player, card):
        if card.feature == '국진':
            if player.is_human:
                while True:
                    decided_type = input('\'멍\'과 \'피\' 중에서 국진을 놓을 곳을 입력하세요 : ')
                    if decided_type in ['멍', '피']: break
            elif not self.is_human:
                decided_type = '피' #ai가 들어갈 부분    
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
            double = filter_cards(lambda c: c.feature in ['쌍', '국진', '보너스'], other.matched['피'])
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
    
    def hit_and_draw(self, player, turn):
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
                move_card(self.deck, player.hand, self.deck[0])
        
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
                move_card(self.deck, self.ground, self.deck[0])
        
        able_on_ground = filter_cards(lambda c: c.month == drawn.month, self.ground)
        move_card(self.deck, self.ground, drawn)
        
        if len(able_on_ground) == 3: 
            if hit in able_on_ground: #따닥
                have_to_choose = False
                temporarily_matched += candidates_for_hit
                if turn != LAST_TURN: rob_count += 1
            
            elif hit not in able_on_ground:    
                for target in able_on_ground:
                    temporarily_matched.append(target)
                temporarily_matched.append(drawn)
                rob_count += 1
                if target.month in player.fucked: rob_count += 1
                        
        elif len(able_on_ground) == 2:
            if hit in able_on_ground: #뻑
                if turn != LAST_TURN:
                    temporarily_matched = []
                    player.memorize_fuck(hit.month)
                    if len(player.fucked) == 3: #삼뻑
                        self.three_fuck = True
                        return None
                    if turn == 1: #첫뻑
                        player.money += 2 * FIRST_FUCK
                        for other in self.get_others(player): other.money -= FIRST_FUCK
                elif turn == LAST_TURN:
                    temporarily_matched = able_on_ground[:]

                
            elif hit not in able_on_ground:    
                have_to_choose = True
                candidates_for_drawn = able_on_ground[:]
                temporarily_matched.append(drawn)    
                
        elif len(able_on_ground) == 1:
            if hit in able_on_ground: #쪽
                temporarily_matched.append(hit)
                temporarily_matched.append(drawn)
                if turn != LAST_TURN: rob_count += 1
            
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
            if turn != LAST_TURN: rob_count += 1 
        
        self.rob_matched_from_others(player, rob_count)
        return None
    
    
    
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
    game.play()     
