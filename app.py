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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/json,*/*',
    }
    url_base = url_base.rstrip('/')
    target_f = float(size_num)
    
    for kw in k_list:
        try:
            if kw:
                search_term = urllib.parse.quote_plus(kw)
            else:
                search_term = "womens+running+shoes" if gender == 'USW' else "running+shoes"
                
            search_url = f"{url_base}/search?q={search_term}&type=product"
            req = urllib.request.Request(search_url, headers=headers)
            html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
            handles = list(dict.fromkeys(re.findall(r'href="[^"]*/products/([^"?/#]+)', html)))
            kl_words = [w.lower() for w in kw.split()]
            
            fetch_count = 0
            for h in handles:
                hl = h.lower().replace('-', ' ')
                if kl_words and not all(w in hl for w in kl_words):
                    continue
                    
                if fetch_count >= 30:
                    break
                    
                try:
                    p_url = f"{url_base}/products/{h}"
                    j_req = urllib.request.Request(f"{p_url}.js", headers=headers)
                    j_data = json.loads(urllib.request.urlopen(j_req, timeout=6).read().decode('utf-8'))
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
                        clean_title = re.sub(r'\d+(\.\d+)?\s*(UK|EU|EUR|CM|MM)', '', clean_title, flags=re.IGNORECASE)
                        v_nums_str = re.findall(r'\d+\.?\d*', clean_title)
                        if not v_nums_str: continue
                            
                        v_nums = [float(x) for x in v_nums_str]
                        match = False
                        
                        if gender == 'USM':
                            if v_nums[0] == target_f: match = True
                            elif len(v_nums) >= 2 and min(v_nums[:2]) == target_f: match = True
                        elif gender == 'USW':
                            if is_womens:
                                if v_nums[0] == target_f: match = True
                            else:
                                if len(v_nums) >= 2:
                                    if max(v_nums[:2]) == target_f or v_nums[0] == (target_f - 1.5): match = True
                                else:
                                    if v_nums[0] == (target_f - 1.5): match = True
                                    
                        if match:
                            p = float(v.get('price', 0)) / 100
                            v_id = v.get('id')
                            final_url = f"{p_url}?variant={v_id}" if v_id else p_url
                            res.append({"store": name, "title": t, "price": p, "url": final_url})
                            seen_titles.add(tl)
                            break
                except: pass
        except: pass
        # 스토어 보안망을 우회하기 위한 사람 흉내내기 (0.1초 딜레이)
        time.sleep(0.1)
        
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
        # 동시다발적 폭격을 막고 스토어당 1개의 안전한 통로만 사용하도록 제한
        with ThreadPoolExecutor(max_workers=len(stores)) as executor:
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
