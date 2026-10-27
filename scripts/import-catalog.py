"""Build local catalog from original verified records and CC BY 4.0 Scento export.
No web scraping. Re-run after updating the licensed JSONL snapshot.
"""
import json,re,unicodedata
from pathlib import Path
root=Path(__file__).resolve().parent.parent
base=json.loads((root/'data/sources/maison-curated.json').read_text())
source=[json.loads(l) for l in (root/'data/sources/scento-perfumes.jsonl').read_text().splitlines() if l]
def normal(s):
 s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower().replace('replica','')
 s=re.sub(r'\b(eau de parfum|eau de toilette|eau de cologne|edp|edt|cologne)\b','',s)
 return re.sub('[^a-z0-9]','',s)
def brand(s):return normal(s).replace('maisonmartinmargiela','maisonmargiela').replace('latt afaperfumes','lattafa').replace('lattafaperfumes','lattafa')
def key(r):return brand(r['brand']),normal(r['name'])
# Explicit additions selected for the user's leather/amber/woody brief. Price/size and notes are checked at the cited pages.
for id,b,n,p,size,notes,url in [
 ('ms-051','Afnan','Rare Carbon Eau de Parfum',50,100,['Leather','Violet leaf','Cinnamon bark','Nutmeg','Rose','Violet','Cedarwood','Oud wood','Vetiver','Sandalwood','Amber'],'https://us.afnan.com/products/rare-carbon?currency=USD&variant=46072198758617'),
 ('ms-052','Rasasi','La Yuqawam Pour Homme Eau de Parfum',69,75,['Raspberry','Saffron','Thyme','Jasmine','Artemisia','Leather','Suede','Amber','Woody notes'],'https://redbagstore.com/products/la-yuqawam-rasasi-eau-de-parfum-for-men-spray-2-53oz-75ml'),
 ('ms-053','Maison Alhambra','Toscano Leather Eau de Parfum',16.99,80,['Saffron','Thyme','Leather','Woody notes','Incense','Raspberry','Jasmine','Amber'],'https://mapleprime.com/products/maison-alhambra-toscano-leather-eau-de-parfum-for-unisex')]:
 r=dict(base[0]);r.update(id=id,brand=b,name=n,priceUsd=p,bottleSizeMl=size,notes=notes,sourceUrls=[url],priceSourceUrl=url,families=['leather','amber','woody','spicy'],climates=['cool','cold'],occasions=['evening','date night','special events'],intensity=None,dataCaveat=None,concentration='Eau de Parfum',image=None,imageLicense=None,verifiedAt='2026-10-26');base.append(r)
seen={key(r) for r in base}
family_map={'Wood & Root':['woody'],'White Bloom':['floral'],'Petal Garden':['floral'],'Green Leaf':['fresh'],'Velvet Sweet':['gourmand'],'Spice Route':['spicy'],'Sunlit Citrus':['citrus'],'Amber & Resin':['amber'],'Powder Veil':['floral'],'Skin Musk':['fresh'],'Smoke & Leather':['leather'],'Oud Court':['woody'],'Salt & Mineral':['aquatic'],'Orchard Fruit':[]}
for s in sorted(source,key=lambda s:s.get('popularity_rank') or 99999):
 r={'brand':s['house'],'name':s['name']}
 if key(r) in seen:continue
 conc={'eau-de-parfum':'Eau de Parfum','eau-de-toilette':'Eau de Toilette','eau-de-cologne':'Eau de Cologne','extrait':'Extrait de Parfum','parfum':'Parfum'}.get(s.get('concentration'))
 # Concentrations identify variants; append the source concentration when available.
 if conc and normal(conc) not in normal(r['name']):r['name']+=' '+conc
 # Only the publisher's primary and secondary accord groups become family
 # tags. A single ingredient note is not enough to relabel the whole scent.
 families=set(family_map.get(s.get('family'),[])+family_map.get(s.get('secondary_family'),[]))
 # Keep records with an unmapped accord too; an empty list means family data
 # is unknown to this taxonomy, not that the product should disappear.
 climates=[]
 for season,c in [('summer','hot'),('spring','mild'),('autumn','cool'),('winter','cold')]:
  if season in (s.get('seasons') or []):climates.append(c)
 times=s.get('times_of_day') or [];occasions=[]
 if 'day' in times:occasions+=['daily','office']
 if 'evening' in times or 'night' in times:occasions+=['evening','date night','special events']
 r.update(id='scento-'+s['id'],concentration=conc,families=sorted(families),notes=s.get('notes') or None,climates=climates,occasions=occasions,intensity=None,priceUsd=None,bottleSizeMl=None,image=None,imageLicense=None,sourceUrls=[s['url']],priceSourceUrl=None,verifiedAt=None,notesStatus='publisher-sourced',guidanceBasis="Scent families follow the publisher's primary and secondary accord groups; ingredient notes remain separate. Climate and occasion are editorial mappings of seasons and time-of-day guidance.",dataCaveat=None,dataProvider='Scento',dataLicense='CC BY 4.0',dataLicenseUrl='https://creativecommons.org/licenses/by/4.0/',providerId=s['id'])
 if key(r) in seen:continue
 seen.add(key(r));base.append(r)
photo_file=root/'data/sources/photo-manifest.json'
if photo_file.exists():
 photos={p['fragranceId']:p for p in json.loads(photo_file.read_text())}
 for r in base:
  if r['id'] in photos:r.update({k:v for k,v in photos[r['id']].items() if k!='fragranceId'})
(root/'src/data/fragrances.json').write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n')
print('Catalog:',len(base),'unique fragrances;',sum(r['priceUsd'] is not None for r in base),'sourced USD estimates')
