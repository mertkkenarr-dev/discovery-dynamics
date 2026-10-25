"""Pilot özeti: GetItems + histogram çıktılarından yapı ve kalite göstergeleri (hipotez testi YOK).

Kullanım: cd scripts && python p01_pilot_ozet.py
"""
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, ".")
from ortak import INTERIM, RAW, jsonl_gz_oku  # noqa: E402  (betik dizininden çalıştırılır)

ev=pd.read_parquet(INTERIM/'evren.parquet'); pl=pd.read_csv(INTERIM/'pilot_appid.csv')
k=ev[(ev.yil_set>=2018)&(ev.yil_set<=2025)].copy()
k['kademe_set']=pd.cut(k.inceleme_set,[-1,9,99,499,4999,np.inf],labels=['T0','T1','T2','T3','T4']).astype(str)
N=k.groupby(['yil_set','kademe_set']).size().rename('N').reset_index()
pl=pl.merge(N,on=['yil_set','kademe_set']); pl['w']=pl.N/25
it={x['_istenen_appid']:x for x in jsonl_gz_oku(RAW/'steam_getitems/items.jsonl.gz')}
kid=lambda d: str(d.get('creator_clan_account_id') or d.get('name'))
rows=[]
for a in pl.appid:
    x=it.get(a,{}); r=x.get('release') or {}; bi=x.get('basic_info') or {}; langs=x.get('supported_languages') or []
    rows.append(dict(appid=a,type=x.get('type'),
      rel=pd.to_datetime(r.get('steam_release_date'),unit='s') if r.get('steam_release_date') else pd.NaT,
      orig=pd.to_datetime(r.get('original_steam_release_date'),unit='s') if r.get('original_steam_release_date') else pd.NaT,
      ea=bool(x.get('is_early_access')), demo=bool((x.get('related_items') or {}).get('demo_appid')),
      dev='|'.join(sorted(kid(d) for d in bi.get('developers',[]))), pub='|'.join(sorted(kid(d) for d in bi.get('publishers',[]))),
      dev_id_var=bool(bi.get('developers')) and all(d.get('creator_clan_account_id') for d in bi.get('developers',[])),
      ntag=len(x.get('tags') or []), schinese=any(l.get('elanguage')==6 and l.get('supported') for l in langs), nlang=sum(1 for l in langs if l.get('supported')),
      rc=((x.get('reviews') or {}).get('summary_filtered') or {}).get('review_count')))
p=pl.merge(pd.DataFrame(rows),on='appid')
W=lambda m: round((p.w*m).sum()/p.w.sum()*100,1)
print('Ağırlıklı tür payı (%): oyun',W(p.type==0),'playtest(12)',W(p.type==12),'yazılım(6)',W(p.type==6),'diğer',W(~p.type.isin([0,12,6])))
print('yıllara göre oyun-dışı payı:', {int(y):round(((d.w*(d.type!=0)).sum()/d.w.sum())*100,1) for y,d in p.groupby('yil_set')})
o=p[p.type==0].copy()
print('çıkış yılı uyumu (set vs GetItems): %', round((o.rel.dt.year==o.yil_set).mean()*100,1))
print('geliştirici kimliği olan %',round(o.dev_id_var.mean()*100,1),' dev==pub %',round((o.dev==o.pub).mean()*100,1))
print('EA ile başlamış %',round(o.orig.notna().mean()*100,1),' şu an EA %',round(o.ea.mean()*100,1),' demo görünen %',round(o.demo.mean()*100,1))
print('etiket sayısı medyan',o.ntag.median(),' Çince %',round(o.schinese.mean()*100,1),' dil medyan',o.nlang.median())
H={x['appid']:x for x in jsonl_gz_oku(RAW/'steam_histogram/histogram.jsonl.gz')}
hs=[]
for a,rel in zip(o.appid,o.rel):
    h=H.get(a,{}); r=h.get('results') or {}; ro=r.get('rollups') or []
    tot=sum(z['recommendations_up']+z['recommendations_down'] for z in ro); r365=0
    if ro and pd.notna(rel):
        ts=pd.to_datetime([z['date'] for z in ro],unit='s'); v=np.array([z['recommendations_up']+z['recommendations_down'] for z in ro])
        r365=int(v[(ts>=rel.normalize()-pd.Timedelta(days=31))&(ts<rel+pd.Timedelta(days=365))].sum())
    hs.append(dict(appid=a,hsucc=h.get('success'),rtype=r.get('rollup_type'),nroll=len(ro),htot=tot,r365=r365))
o=o.merge(pd.DataFrame(hs),on='appid')
print('histogram success', o.hsucc.value_counts(dropna=False).to_dict(),' rollup tipi', o.rtype.value_counts(dropna=False).to_dict())
q=o[o.rc>0]; ratio=q.htot/q.rc
print('R12 oran histogram/özet: medyan',round(ratio.median(),3),' 0.8-1.05 dışı %',round((~ratio.between(0.8,1.05)).mean()*100,1),' (rc>=50 içinde %',round((~ratio[q.rc>=50].between(0.8,1.05)).mean()*100,1),')')
print('çeyrekler oran', ratio.quantile([.1,.25,.5,.75,.9]).round(2).tolist())
z=o[(o.nroll==0)&(o.rc>0)]; print('rollup yok ama rc>0:', len(z), 'rc medyan/maks', z.rc.median(), z.rc.max())
gozlem=(pd.Timestamp('2026-10-22')-o.rel).dt.days
print('>=395 gün gözlenmiş %',round((gozlem>=395).mean()*100,1),'; 2025 çıkışlılarda %',round((gozlem[o.rel.dt.year==2025]>=395).mean()*100,1))
o['hit']=o.r365>=500
print('Ağırlıklı hit oranı yıla göre:', {int(y):round((d.w*d.hit).sum()/d.w.sum()*100,1) for y,d in o[gozlem>=395].groupby(o.rel.dt.year)})
print('Ağırlıklı r365 kademeleri (%):', {t:round((o.w*m).sum()/o.w.sum()*100,1) for t,m in [('T0',o.r365<10),('T1',o.r365.between(10,99)),('T2',o.r365.between(100,499)),('T3',o.r365.between(500,4999)),('T4',o.r365>=5000)]})
o.to_parquet(INTERIM/'pilot_ozet.parquet',index=False)
