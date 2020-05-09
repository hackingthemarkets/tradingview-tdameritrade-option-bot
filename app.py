from tda import auth, client
import os, json, datetime
from chalice import Chalice
from chalicelib import config

app = Chalice(app_name='trading-view-tdameritrade-option-alert')

token_path = os.path.join(os.path.dirname(__file__), 'chalicelib', 'token')

c = auth.client_from_token_file(token_path, config.api_key)

@app.route('/quote/{symbol}')
def quote(symbol):
    response = c.get_quote(symbol)

    return response.json()

@app.route('/option/chain/{symbol}')
def option_chain(symbol):
    response = c.get_option_chain(symbol)

    return response.json()


@app.route('/option/order', methods=['POST'])
def option_order():
    webhook_message = app.current_request.json_body

    print(webhook_message)
    
    if 'passphrase' not in webhook_message:
        return {
            "code": "error",
            "message": "Unauthorized, no passphrase"
        }

    if webhook_message['passphrase'] != config.passphrase:
        return {
            "code": "error",
            "message": "Invalid passphrase"
        }
    
    order_spec = {
        "complexOrderStrategyType": "NONE",
        "orderType": "LIMIT",
        "session": "NORMAL",
        "price": webhook_message["price"],
        "duration": "DAY",
        "orderStrategyType": "SINGLE",
        "orderLegCollection": [
            {
            "instruction": "BUY_TO_OPEN",
            "quantity": webhook_message["quantity"],
            "instrument": {
                "symbol": webhook_message["symbol"],
                "assetType": "OPTION"
            }
            }
        ]
    }

    response = c.place_order(config.account_id, order_spec)

    return {
        "code": "ok"
    }