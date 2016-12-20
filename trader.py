from api import Quadriga
from math import floor
import time

# apiKey=input("Enter the api key: ")
# apiSecret=input("Enter the api secret: ")
apiKey = ''
apiSecret = ''
clientID=164993
usd = 500001
order_price_limit_100 = 78500
trader = Quadriga(apiKey, apiSecret, clientID)
my_order_id = None
my_order_price = None

def convert(str):
    l = str.split('.')
    return int(l[0])*100+int(l[1])

def _convert(num):
    return str(int(num/100))+'.'+('0'+str(num%100) if len(str(num%100))<2 else str(num%100))

while True:
    # get my order info
    if my_order_id is not None:
        my_order_info = trader.lookup_order(my_order_id)
        my_order_price = convert(my_order_info[0]['price'])
        if my_order_info[0]['status'] == '2':
            print('Order Complete! {}'.format(my_order_info))
            #break
        elif my_order_info[0]['status'] == '1':
            print('Partially Full-filled! {}'.format(my_order_info))

    orders = trader.get_order_book(book='btc_usd', group=1)
    bids = orders['bids']
    asks = orders['asks']
    bids = sorted(bids, key = lambda d: float(d[0]), reverse=True)
    asks = sorted(asks, key = lambda d: float(d[0]))
    highest_ask_100 = convert(asks[0][0])
    highest_bid_100 = convert(bids[0][0])
    second_highest_bid_100 = convert(bids[1][0]) if len(bids)>=2 else None


    # get a new order if (1) no order placed (2) there's a higher bid than us (3) our bid is not the second highest bid + 0.01
    if my_order_id is None or my_order_price < highest_bid_100 or (my_order_price == highest_bid_100 and second_highest_bid_100 is not None and
                                                                       my_order_price - second_highest_bid_100 > 1):

        if my_order_id is not None and my_order_price == highest_bid_100 and second_highest_bid_100 is not None and my_order_price - second_highest_bid_100 > 1:
            highest_bid_100 = second_highest_bid_100
            cancel_rv = trader.cancel_order(my_order_id)
            print('Order Cancelled! {}'.format(cancel_rv))
        elif my_order_id is not None and my_order_price < highest_bid_100:
            cancel_rv = trader.cancel_order(my_order_id)
            print('Order Cancelled! {}'.format(cancel_rv))

        new_order_price_100 = min(highest_bid_100 + 1, highest_ask_100, order_price_limit_100)

        rv = trader.buy_order_limit(floor((usd/new_order_price_100)*1000000.0)/1000000.0, _convert(new_order_price_100), book='btc_usd')
        my_order_id = rv['id']
        print('Order at {} = min(highest_bid + 0.01 = {} + 0.01, lowest_ask = {}, price_limit = {})) '.format(
            _convert(new_order_price_100), _convert(highest_bid_100),
            _convert(highest_ask_100), _convert(order_price_limit_100)))
        print(rv)
        print('\n=================================================================================== \n')

    # sleep for 2 seconds
    time.sleep(10)