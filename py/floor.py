import pandas as pd
def floor_home(floor):
    deck1_5 = 0
    deck6_10 = 0
    deck11_15 = 0
    deck16 = 0
    for i in floor:
        if 5 >= i >= 1:
            deck1_5 += 1
        elif 10 >= i >= 6:
            deck6_10 += 1
        elif 15 >= i >= 11:
            deck11_15 += 1
        else:
            deck16 += 1
    dk = [deck1_5, deck6_10, deck11_15, deck16]
    labels = ['1층~5층', '6층~10층', '11층~15층', '16층 이상']
    return pd.DataFrame(dk, index = labels)