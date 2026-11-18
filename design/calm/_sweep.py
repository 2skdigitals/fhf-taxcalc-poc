from playwright.sync_api import sync_playwright
import json
W=[320,328,360,390,414,430,480,540,568,600,640,700,721,768,820,900,944,1024,1100,1200,1280,1440]
out={}
with sync_playwright() as pw:
    b=pw.chromium.launch(channel="chrome",headless=True)
    for lang in ("zh-HK","en"):
        for part in ("calc","pay","receipt"):
            rows=[]
            for w in W:
                p=b.new_page(viewport={"width":w,"height":240},is_mobile=(w<600),has_touch=(w<600))
                p.goto(f"http://127.0.0.1:8766/index.html?part={part}&lang={lang}",wait_until="load")
                p.wait_for_timeout(200)
                rows.append((w,p.evaluate("()=>document.documentElement.scrollHeight")))
                p.close()
            pk=max(rows,key=lambda r:r[1])
            out[f"{part}/{lang}"]={"peak":pk[1],"at":pk[0],"min":min(r[1] for r in rows)}
    b.close()
json.dump(out,open('heights-final.json','w'),indent=1)
for k,v in out.items(): print(k,v,"peak+55 =",v['peak']+55)
