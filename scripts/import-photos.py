"""Fetch openly licensed photographs from Open Beauty Facts' public JSON API.
Caches responses. Only exact normalized brand/name matches are considered.
Images remain separate CC BY-SA 3.0 works with per-image contributor credit.
"""
import csv,json,re,unicodedata,urllib.request,time,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent.parent
rows=json.loads((root/'src/data/fragrances.json').read_text())
def norm(s):
 s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
 s=re.sub(r'\b(replica|eau de parfum|eau de toilette|eau de cologne|edp|edt|parfum|cologne)\b','',s)
 return re.sub('[^a-z0-9]','',s)
products=list(csv.DictReader((root/'data/sources/open-beauty-facts.csv').open()))
lookup={}
for p in products:lookup.setdefault((norm(p['brand_name']),norm(p['name'])),p)
requests=[]
for f in rows:
 p=lookup.get((norm(f['brand']),norm(f['name'])))
 if p:requests.append((f,p))
print('Exact photo candidates',len(requests),flush=True)
cache=root/'data/sources/obf';cache.mkdir(exist_ok=True)
images=root/'public/images/bottles';images.mkdir(exist_ok=True)
manifest=[]
review_file=root/'data/sources/photo-review.json'
approved=set(json.loads(review_file.read_text())['approvedIds']) if review_file.exists() else set()
for index,(f,p) in enumerate(requests):
 code=p['ean'];record=cache/(code+'.json')
 try:
  if not record.exists():
   req=urllib.request.Request('https://world.openbeautyfacts.org/api/v2/product/'+code+'.json?fields=code,product_name,brands,images,image_front_url',headers={'User-Agent':'MaisonSillage/1.1 local fragrance guide (open-data photo import)'})
   data=json.loads(subprocess.run(['curl','--fail','--silent','--show-error','--max-time','15','--user-agent','MaisonSillage/1.1 open-data import',req.full_url],capture_output=True,check=True).stdout)
   record.write_text(json.dumps(data))
   time.sleep(.55)
  data=json.loads(record.read_text()).get('product',{})
  title=data.get('product_name','').lower();expected=(f.get('concentration') or '').lower()
  # Reject known edition mismatches. A missing edition in source remains unmapped.
  edt=bool(re.search(r'\bedt\b|eau de toilette',title));edp=bool(re.search(r'\bedp\b|eau de parfum',title))
  if ('eau de parfum' in expected and edt and not edp) or ('eau de toilette' in expected and edp and not edt):continue
  url=data.get('image_front_url')
  if not url:continue
  dest=images/(code+'.jpg')
  if not dest.exists():
   req=urllib.request.Request(url,headers={'User-Agent':'MaisonSillage/1.1 local fragrance guide'})
   dest.write_bytes(subprocess.run(['curl','--fail','--silent','--show-error','--max-time','15',url],capture_output=True,check=True).stdout)
  # Author is the uploader of the selected original image.
  selected=next((v for k,v in data.get('images',{}).items() if k.startswith('front_')),{});author=data.get('images',{}).get(str(selected.get('imgid')),{}).get('uploader','Open Beauty Facts contributors')
  entry=dict(fragranceId=f['id'],image='/images/bottles/'+code+'.jpg',imageLicense='CC BY-SA 3.0',imageLicenseUrl='https://creativecommons.org/licenses/by-sa/3.0/',imageSourceUrl=p['obf_url'],imageAuthor=author,imageSourceTitle=data.get('product_name') or p['name'],barcode=code)
  if f['id'] in approved:manifest.append(entry)
 except Exception as e:print('Skipped',code,type(e).__name__,flush=True)
 if index%10==0:print('Progress',index+1,'/',len(requests),'photos',len(manifest),flush=True)
(root/'data/sources/photo-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
byid={p['fragranceId']:p for p in manifest}
for f in rows:
 if f['id'] in byid:f.update({k:v for k,v in byid[f['id']].items() if k!='fragranceId'})
(root/'src/data/fragrances.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print('Imported',len(manifest),'licensed photos',flush=True)
