import os, json, urllib.request, re, ssl
from flask import Flask, request, jsonify, render_template

try: _create_unverified_https_context = ssl._create_unverified_context
except AttributeError: pass
else: ssl._create_default_https_context = _create_unverified_https_context

app = Flask(__name__)

def scan_store(name, url_base, kw, gender, size_num):
    res = []
    seen_titles = set()
    try:
        url_base = url_base.rstrip('/')
        search_term = kw.replace(' ', '+') if kw.strip() else "running+shoes"
        search_url = f"{url_base}/search?q={search_term}"
        
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        handles = list(dict.fromkeys(re.findall(r'href="[^"]*/products/([^"?/#]+)', html)))
        
        kl = kw.lower().strip()
        target_f = float(size_num)
        
        for h in handles[:25]:
            try:
                p_url = f"{url_base}/products/{h}"
                j_req = urllib.request.Request(f"{p_url}.js", headers={'User-Agent': 'Mozilla/5.0'})
                j_data = json.loads(urllib.request.urlopen(j_req, timeout=5).read().decode('utf-8'))
                t = j_data.get('title', h)
                tl = t.lower()
                
                if kl and kl not in tl: continue
                is_womens_shoe = 'women' in tl or 'wmns' in tl
                is_unisex_shoe = 'unisex' in tl
                
                if gender == 'USM' and is_womens_shoe: continue
                if gender == 'USW' and not is_womens_shoe and not is_unisex_shoe and ('men' in tl): continue
                if 'wide' in tl or '2e' in tl or '4e' in tl: continue
                if tl in seen_titles: continue
                
                for v in j_data.get('variants', []):
                    v_title = v.get('title', '')
                    if not v.get('available'): continue
                    
                    clean_title = re.sub(r'(UK|EU|EUR|CM|MM)\s*\d+(\.\d+)?', '', v_title, flags=re.IGNORECASE)
                    clean_title = re.sub(r'\d+(\.\d+)?\s*(UK|EU|EUR|CM|MM)', '', clean_title, flags=re.IGNORECASE)
                    
                    v_nums_str = re.findall(r'\d+\.?\d*', clean_title)
                    if not v_nums_str: continue
                        
                    v_nums = [float(x) for x in v_nums_str]
                    match = False
                    
                    if gender == 'USM':
                        if v_nums[0] == target_f: match = True
                    elif gender == 'USW':
                        if is_womens_shoe:
                            if v_nums[0] == target_f: match = True
                        else:
                            if len(v_nums) >= 2:
                                if v_nums[1] == target_f or v_nums[0] == (target_f - 1.5): match = True
                            else:
                                if v_nums[0] == (target_f - 1.5): match = True
                                
                    if match:
                        p = float(v.get('price', 0)) / 100
                        v_id = v.get('id')
                        final_url = f"{p_url}?variant={v_id}" if v_id else p_url
                        res.append({"store": name, "title": t, "price": f"${p:.2f}", "url": final_url})
                        seen_titles.add(tl)
                        break
            except Exception: pass
    except Exception: pass
    return res

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/scan', methods=['POST'])
def scan_api():
    try:
        req = request.get_json(silent=True) or {}
        kw = req.get('k', '')
        gender = req.get('g', 'USM')
        size_num = req.get('s', '9.5')
        stores = req.get('stores', [])
        
        data = []
        for s in stores:
            try: data.extend(scan_store(s['name'], s['url'], kw, gender, size_num))
            except Exception: pass
        return jsonify(data)
    except Exception:
        return jsonify([])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
