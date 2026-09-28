import os

SAFE_HTML = """(L)!DOCTYPE html(R)
(L)html(R)
(L)head(R)
    (L)meta charset="UTF-8"(R)
    (L)meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover"(R)
    (L)meta name="apple-mobile-web-app-capable" content="yes"(R)
    (L)meta name="apple-mobile-web-app-status-bar-style" content="default"(R)
    (L)title(R)ShoeTracker Pro(L)/title(R)
    (L)style(R)
        body { font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif; padding: 20px 15px; background: #f1f5f9; color: #0f172a; user-select: none; margin: 0; -webkit-tap-highlight-color: transparent; }
        .card { background: #ffffff; padding: 25px 20px; border-radius: 24px; max-width: 900px; margin: auto; box-shadow: 0 20px 40px -10px rgba(0,0,0,0.08); border: 1px solid rgba(255,255,255,0.8); }
        h2 { text-align: center; font-size: 24px; font-weight: 800; color: #0f172a; letter-spacing: -0.5px; margin-bottom: 25px; margin-top: 0; }
        .input-group { margin-bottom: 25px; position: relative; }
        label.section-title { font-weight: 700; font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 1.2px; display: block; margin-bottom: 10px; }
        input[type='text'] { padding: 14px 18px; width: 100%; border: 1.5px solid #e2e8f0; border-radius: 14px; font-size: 15px; font-weight: 500; background: #f8fafc; color: #0f172a; box-sizing: border-box; outline: none; transition: all 0.25s; }
        input[type='text']:focus { border-color: #3b82f6; background: #ffffff; box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15); }
        
        .checkbox-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px; }
        .chk-wrapper { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; color: #334155; cursor: pointer; }
        .chk-wrapper input[type='checkbox'] { width: 18px; height: 18px; cursor: pointer; accent-color: #3b82f6; }

        /* 🔥 iOS 전용 휠 다이얼 버그 수정 (높이 138px 고정 & 클리핑 방지) 🔥 */
        .size-action-row { display: flex; flex-direction: column; gap: 12px; }
        .picker-container { width: 100%; height: 138px; background: #f8fafc; border-radius: 18px; border: 1.5px solid #e2e8f0; position: relative; overflow: hidden; display: flex; justify-content: center; align-items: center; }
        .picker-mask { position: absolute; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; z-index: 2; background: linear-gradient(to bottom, rgba(248, 250, 252, 0.95) 0%, rgba(248, 250, 252, 0) 30%, rgba(248, 250, 252, 0) 70%, rgba(248, 250, 252, 0.95) 100%); }
        .picker-highlight { position: absolute; top: 50%; transform: translateY(-50%); left: 3%; right: 3%; height: 46px; background: #ffffff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); z-index: 0; pointer-events: none; }
        
        .wheel-col { width: 50%; height: 100%; overflow-y: scroll; scroll-snap-type: y mandatory; scrollbar-width: none; z-index: 1; -webkit-overflow-scrolling: touch; }
        .wheel-col::-webkit-scrollbar { display: none; }
        .wheel-spacer { height: 46px; }
        .wheel-item { height: 46px; line-height: 46px; text-align: center; font-size: 16px; font-weight: 600; color: #94a3b8; scroll-snap-align: center; cursor: pointer; transition: all 0.2s; transform: scale(0.85); opacity: 0.35; }
        .wheel-item.selected { color: #0f172a; font-size: 18px; font-weight: 800; transform: scale(1.05); opacity: 1; }

        .btn-primary { width: 100%; height: 54px; display: flex; flex-direction: row; justify-content: center; align-items: center; gap: 8px; background: linear-gradient(to bottom, #1e293b, #0f172a); border: 1px solid #334155; border-radius: 16px; color: white; font-weight: 800; font-size: 15px; text-transform: uppercase; letter-spacing: 1px; cursor: pointer; box-shadow: 0 4px 0 #020617, 0 8px 15px rgba(0,0,0,0.15); transition: all 0.1s; }
        .btn-primary:active { transform: translateY(4px); box-shadow: 0 0 0 #020617; height: 54px; }
        .btn-stop { background: linear-gradient(to bottom, #ef4444, #dc2626) !important; border: 1px solid #b91c1c !important; box-shadow: 0 4px 0 #7f1d1d !important; }
        .btn-icon { font-size: 18px; }

        #progress-container { display: none; width: 100%; height: 4px; background: #e2e8f0; border-radius: 2px; margin-top: 15px; overflow: hidden; }
        #progress-bar { width: 0%; height: 100%; background: linear-gradient(90deg, #3b82f6, #a855f7, #ec4899); border-radius: 2px; transition: width 0.3s ease; }
        #status { font-weight: 700; color: #64748b; margin-top: 10px; margin-bottom: 0; font-size: 13px; text-align: center; }

        .table-responsive { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; }
        table { width: 100%; border-collapse: separate; border-spacing: 0 10px; margin-top: 10px; min-width: 500px; }
        th { font-size: 11px; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; padding: 0 15px 6px 15px; border: none; }
        td { background: #ffffff; padding: 15px; border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
        td:first-child { border-left: 1px solid #f1f5f9; border-top-left-radius: 14px; border-bottom-left-radius: 14px; }
        td:last-child { border-right: 1px solid #f1f5f9; border-top-right-radius: 14px; border-bottom-right-radius: 14px; }
        
        .badge { padding: 5px 10px; border-radius: 6px; font-size: 10px; font-weight: 800; color: white; white-space: nowrap; }
        .btn-link { padding: 6px 16px; background: #e0f2fe; color: #0284c7; text-decoration: none; border-radius: 100px; font-size: 12px; font-weight: 800; display: inline-block; white-space: nowrap; }
    (L)/style(R)
(L)/head(R)
(L)body(R)
    (L)div class="card"(R)
        (L)h2(R)👟 ShoeTracker Pro(L)/h2(R)
        
        (L)div class="input-group"(R)
            (L)label class="section-title"(R)1. Select Target Stores(L)/label(R)
            (L)div class="checkbox-grid"(R)
                (L)label class="chk-wrapper"(R)(L)input type="checkbox" class="store-cb" value="https://paceathletic.com" data-name="Pace Athletic"(R) Pace Athletic(L)/label(R)
                (L)label class="chk-wrapper"(R)(L)input type="checkbox" class="store-cb" value="https://www.therunningshop.com.au" data-name="The Running Shop"(R) The Running Shop(L)/label(R)
                (L)label class="chk-wrapper"(R)(L)input type="checkbox" class="store-cb" value="https://www.keeponrunning.com.au" data-name="Keep On Running"(R) Keep On Running(L)/label(R)
                (L)label class="chk-wrapper"(R)(L)input type="checkbox" class="store-cb" value="https://shop.therunningcompany.com.au" data-name="Running Company"(R) Running Company(L)/label(R)
            (L)/div(R)
            (L)input type="text" id="custom-url" placeholder="(Optional) Add Shopify URLs, separated by commas (,)" autocomplete="off" spellcheck="false"(R)
        (L)/div(R)

        (L)div class="input-group" id="kw-container"(R)
            (L)label class="section-title"(R)2. Target Keywords (Leave blank for all)(L)/label(R)
            (L)input type="text" id="k" placeholder="e.g. Novablast" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"(R)
        (L)/div(R)

        (L)div class="input-group"(R)
            (L)label class="section-title"(R)3. Target Size & Scan(L)/label(R)
            (L)div class="size-action-row"(R)
                (L)div class="picker-container" id="picker-main"(R)
                    (L)div class="picker-mask"(R)(L)/div(R)
                    (L)div class="picker-highlight"(R)(L)/div(R)
                    (L)div class="wheel-col" id="wheel-gender"(R)
                        (L)div class="wheel-spacer"(R)(L)/div(R)
                        (L)div class="wheel-item selected" data-val="USM"(R)USM (Men)(L)/div(R)
                        (L)div class="wheel-item" data-val="USW"(R)USW (Women)(L)/div(R)
                        (L)div class="wheel-spacer"(R)(L)/div(R)
                    (L)/div(R)
                    (L)div class="wheel-col" id="wheel-size"(R)
                        (L)div class="wheel-spacer"(R)(L)/div(R)
                        (L)div class="wheel-spacer" id="bottom-spacer"(R)(L)/div(R)
                    (L)/div(R)
                (L)/div(R)
                (L)button id="scanBtn" class="btn-primary"(R)
                    (L)div class="btn-icon" id="btnIcon"(R)▶(L)/div(R)
                    (L)div id="btnText"(R)SCAN(L)/div(R)
                (L)/button(R)
            (L)/div(R)
            (L)div id="progress-container"(R)(L)div id="progress-bar"(R)(L)/div(R)(L)/div(R)
            (L)p id="status"(R)Ready to scan(L)/p(R)
        (L)/div(R)
        
        (L)div class="table-responsive"(R)
            (L)table class="results-table"(R)
                (L)thead(R)
                    (L)tr(R)
                        (L)th(R)Store(L)/th(R)
                        (L)th(R)Shoe Title(L)/th(R)
                        (L)th id="phead"(R)Price(L)/th(R)
                        (L)th style="text-align:center;"(R)Link(L)/th(R)
                    (L)/tr(R)
                (L)/thead(R)
                (L)tbody id="board"(R)(L)/tbody(R)
            (L)/table(R)
        (L)/div(R)
    (L)/div(R)
    (L)script(R)
        const sizes = [6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0];
        let selGender = 'USM';
        let selSize = '9.5';
        const sizeWheel = document.getElementById('wheel-size');
        const bSpacer = document.getElementById('bottom-spacer');
        sizes.forEach(sz => {
            const div = document.createElement('div');
            div.className = 'wheel-item' + (sz === 9.5 ? ' selected' : '');
            div.dataset.val = sz.toFixed(1);
            div.innerText = sz.toFixed(1);
            sizeWheel.insertBefore(div, bSpacer);
        });

        function setupWheel(colId, onChange) {
            const col = document.getElementById(colId);
            col.addEventListener('scroll', () => {
                const items = col.querySelectorAll('.wheel-item');
                let closest = null;
                let minDiff = Infinity;
                const colCenter = col.getBoundingClientRect().top + col.clientHeight / 2;
                items.forEach(item => {
                    const rect = item.getBoundingClientRect();
                    const itemCenter = rect.top + rect.height / 2;
                    const diff = Math.abs(colCenter - itemCenter);
                    if (diff < minDiff) { minDiff = diff; closest = item; }
                });
                items.forEach(i => i.classList.remove('selected'));
                if (closest) { closest.classList.add('selected'); onChange(closest.dataset.val); }
            }, { passive: true });
        }
        setupWheel('wheel-gender', val => { selGender = val; });
        setupWheel('wheel-size', val => { selSize = val; });

        let abortCtrl = null;
        let isScanning = false;
        let progInt = null;
        
        document.getElementById('scanBtn').onclick = function() {
            const btn = this;
            const icon = document.getElementById('btnIcon');
            const text = document.getElementById('btnText');
            const stat = document.getElementById('status');
            const brd = document.getElementById('board');
            const pCont = document.getElementById('progress-container');
            const pBar = document.getElementById('progress-bar');
            const pickerMain = document.getElementById('picker-main');
            const k_val = document.getElementById('k').value.trim();
            
            if (isScanning) {
                if (abortCtrl) abortCtrl.abort();
                return;
            }
            
            let activeStores = [];
            document.querySelectorAll('.store-cb:checked').forEach(cb => {
                activeStores.push({name: cb.dataset.name, url: cb.value});
            });
            
            const customUrlRaw = document.getElementById('custom-url').value.trim();
            if (customUrlRaw) {
                const urls = customUrlRaw.split(',').map(u => u.trim()).filter(u => u);
                urls.forEach(u => {
                    let cName = 'Custom Store';
                    try { cName = new URL(u).hostname.replace('www.', ''); } catch(e){}
                    activeStores.push({name: cName, url: u});
                });
            }
            
            if(activeStores.length === 0) {
                alert('Please select at least one store!');
                return;
            }

            const fullSize = selGender + ' ' + selSize;
            isScanning = true;
            pickerMain.style.pointerEvents = 'none';
            pickerMain.style.opacity = '0.5';
            
            icon.innerText = '⏹';
            text.innerText = 'STOP';
            btn.classList.add('btn-stop');
            
            let searchStr = k_val ? "'" + k_val + "'" : "ALL SHOES";
            stat.innerText = "🟢 Scanning " + searchStr + " (" + activeStores.length + " Stores)...";
            stat.style.color = '#3b82f6';
            
            brd.innerHTML = '';
            document.getElementById('phead').innerText = 'Price (' + fullSize + ')';
            
            pCont.style.display = 'block';
            pBar.style.width = '0%';
            let progW = 0;
            clearInterval(progInt);
            progInt = setInterval(() => {
                if (progW < 90) { progW += (90 - progW) / 10; pBar.style.width = progW + '%'; }
            }, 500);

            abortCtrl = new AbortController();
            fetch('/api/scan', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({k: k_val, g: selGender, s: selSize, stores: activeStores}),
                signal: abortCtrl.signal
            })
            .then(res => res.json())
            .then(data => {
                clearInterval(progInt);
                pBar.style.width = '100%';
                setTimeout(() => { pCont.style.display = 'none'; }, 800);
                
                let html = '';
                if(data.length === 0) {
                    html = '(L)tr(R)(L)td colspan="4" style="text-align:center; padding:20px; font-weight:600; color:#94a3b8;"(R)No matching shoes found.(L)/td(R)(L)/tr(R)';
                } else {
                    data.forEach(item => {
                        let bg = '#64748b';
                        if(item.store.includes('Running Shop')) bg = '#ef4444';
                        else if(item.store.includes('Keep On')) bg = '#f59e0b';
                        else if(item.store.includes('Running Company')) bg = '#6366f1';
                        else if(item.store.includes('Pace')) bg = '#0f172a';
                        
                        html += '(L)tr(R)';
                        html += '(L)td(R)(L)span class="badge" style="background:' + bg + '"(R)' + item.store + '(L)/span(R)(L)/td(R)';
                        html += '(L)td(R)(L)b style="color:#0f172a; font-size:14px;"(R)' + item.title + '(L)/b(R)(L)/td(R)';
                        html += '(L)td style="color:#10b981; font-weight:800; font-size:15px;"(R)' + item.price + '(L)/td(R)';
                        html += '(L)td style="text-align:center;"(R)(L)a href="' + item.url + '" target="_blank" class="btn-link"(R)Store(L)/a(R)(L)/td(R)';
                        html += '(L)/tr(R)';
                    });
                }
                brd.innerHTML = html;
                stat.innerText = '✅ Scan Complete!';
                stat.style.color = '#10b981';
            })
            .catch((err) => {
                clearInterval(progInt);
                pCont.style.display = 'none';
                if (err.name === 'AbortError') {
                    stat.innerText = '🛑 Scan Stopped by User';
                } else {
                    stat.innerText = '🔴 Error occurred!';
                }
                stat.style.color = '#ef4444';
            })
            .finally(() => {
                isScanning = false;
                icon.innerText = '▶';
                text.innerText = 'SCAN';
                btn.classList.remove('btn-stop');
                pickerMain.style.pointerEvents = 'auto';
                pickerMain.style.opacity = '1';
            });
        };
    (L)/script(R)
(L)/body(R)
(L)/html(R)"""

os.makedirs(os.path.expanduser("~/Desktop/ShoeCloud/templates"), exist_ok=True)
with open(os.path.expanduser("~/Desktop/ShoeCloud/templates/index.html"), "w", encoding="utf-8") as f:
    f.write(SAFE_HTML.replace("(L)", "<").replace("(R)", ">"))
print("✅ 아이폰 휠 다이얼 버그 수정 완료!")
