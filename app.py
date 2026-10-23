import os, json, urllib.request, re, ssl, urllib.parse, time
from flask import Flask, request, jsonify, render_template
from concurrent.futures import ThreadPoolExecutor, as_completed

try: _create_unverified_https_context = ssl._create_unverified_context
except AttributeError: pass
else: ssl._create_default_https_context = _create_unverified_https_context

app = Flask(__name__)

DB_FILE = 'shoe_db.json'
DEFAULT_DB = {
    "daily": "Novablast, Pegasus, Clifton, Ghost, Ultraboost, Vomero Plus, Deviate nitro, Ride, Cloud monster, Adizero EVO SL, Rebel V5",
    "max": "Nimbus, 1080, Bondi, Invincible, Ghost Max, Vomero Premium, Glycerin Max, Magmax Nitro",
    "racing": "Vaporfly, Alphafly, Metaspeed, Endorphin Pro, Endorphin Elite, Cloudboom Strike",
    "super": "Superblast, SC Trainer, Megablast, Cloudboom Echo"
}

def get_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except: pass
    return DEFAULT_DB

@app.route('/api/config', methods=['GET', 'POST'])
def config_api():
    if request.method == 'POST':
        new_data = request.get_json(silent=True)
        if new_data:
            with open(DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, ensure_ascii=False)
            return jsonify({"status": "ok"})
    return jsonify(get_db())

def process_store_keywords(name, url_base, k_list, gender, size_num):
    res = []
    seen_titles = set()
    
    # 🔥 브라우저 완벽 위장 헤더
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    headers_json = {
        'User-Agent': headers['User-Agent'],
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    url_base = url_base.rstrip('/')
    target_f = float(size_num)
    
    for kw in k_list:
        kw = kw.strip()
        kw_nospace = kw.lower().replace(' ', '').replace('-', '')
        search_term = urllib.parse.quote_plus(kw) if kw else ("womens+running+shoes" if gender == 'USW' else "running+shoes")
        
        handles = []
        try:
            s_url = f"{url_base}/search?q={search_term}&type=product"
            req = urllib.request.Request(s_url, headers=headers)
            html = urllib.request.urlopen(req, timeout=8).read().decode('utf-8')
            handles.extend(re.findall(r'/products/([a-zA-Z0-9\-]+)', html))
            handles.extend(re.findall(r'"handle"\s*:\s*"([a-zA-Z0-9\-]+)"', html))
        except: pass
        
        if not handles:
            try:
                s_url = f"{url_base}/search/suggest.json?q={search_term}&resources[type]=product"
                req = urllib.request.Request(s_url, headers=headers_json)
                s_data = json.loads(urllib.request.urlopen(req, timeout=5).read().decode('utf-8'))
                for p in s_data.get('resources', {}).get('results', {}).get('products', []):
                    if p.get('handle'): handles.append(p.get('handle'))
            except: pass

        handles = list(dict.fromkeys([h for h in handles if h and len(h) > 3]))
        
        fetch_count = 0
        # 🔥 IP 차단 방지를 위해 검사 개수를 극도로 제한 (키워드 매칭 시 최대 4개, 전체 검색 시 8개)
        max_fetches = 4 if kw else 8  
        
        for h in handles:
            hl_compact = h.lower().replace('-', '')
            
            if kw_nospace and kw_nospace not in hl_compact:
                continue
                
            if fetch_count >= max_fetches:
                break
                
            try:
                p_url = f"{url_base}/products/{h}"
                j_req = urllib.request.Request(f"{p_url}.js", headers=headers_json)
                
                # 🔥 스토어 서버를 자극하지 않는 사람 흉내 딜레이
                time.sleep(0.2) 
                
                j_resp = urllib.request.urlopen(j_req, timeout=5)
                j_data = json.loads(j_resp.read().decode('utf-8'))
                fetch_count += 1
                
                t = j_data.get('title', h)
                tl = t.lower()
                
                is_womens = 'women' in tl or 'wmns' in tl
                is_unisex = 'unisex' in tl
                
                if gender == 'USM' and is_womens: continue
                if gender == 'USW' and not is_womens and not is_unisex and ('men' in tl): continue
                if 'wide' in tl or '2e' in tl or '4e' in tl: continue
                if tl in seen_titles: continue
                
                for v in j_data.get('variants', []):
                    if not v.get('available'): continue
                    
                    v_title = v.get('title', '')
                    clean_title = re.sub(r'(UK|EU|EUR|CM|MM)\s*\d+(\.\d+)?', '', v_title, flags=re.IGNORECASE)
                    v_nums_str = re.findall(r'\d+\.?\d*', clean_title)
                    if not v_nums_str: continue
                        
                    v_nums = [float(x) for x in v_nums_str]
                    match = False
                    
                    if gender == 'USM':
                        if target_f in v_nums: match = True
                    elif gender == 'USW':
                        if is_womens:
                            if target_f in v_nums: match = True
                        else:
                            if v_nums[0] == (target_f - 1.5): match = True
                            elif target_f in v_nums: match = True
                                
                    if match:
                        p = float(v.get('price', 0)) / 100
                        v_id = v.get('id')
                        final_url = f"{p_url}?variant={v_id}" if v_id else p_url
                        res.append({"store": name, "title": t, "price": p, "url": final_url})
                        seen_titles.add(tl)
                        break
            except Exception as e:
                # HTTP 429 에러 발생 시 회피 기동
                if hasattr(e, 'code') and e.code == 429:
                    time.sleep(1)
                pass
                
        # 키워드 변경 시에도 약간의 딜레이
        time.sleep(0.3)
        
    return res

@app.route('/api/scan', methods=['POST'])
def scan_api():
    try:
        req = request.get_json(silent=True) or {}
        k_list = req.get('k_list', [])
        gender = req.get('g', 'USM')
        size_num = req.get('s', '9.5')
        stores = req.get('stores', [])
        
        filtered_k = [k.strip() for k in k_list if k.strip()]
        if not filtered_k: filtered_k = ['']

        data = []
        # 🔥 동시 다발적 7개 스토어 폭격을 막고 최대 4개로 제한
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for s in stores:
                futures.append(executor.submit(process_store_keywords, s['name'], s['url'], filtered_k, gender, size_num))
            for future in as_completed(futures):
                try: data.extend(future.result())
                except: pass
                
        unique_data = []
        seen = set()
        for d in data:
            if d['url'] not in seen:
                seen.add(d['url'])
                unique_data.append(d)
                
        return jsonify(unique_data)
    except Exception:
        return jsonify([])

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
