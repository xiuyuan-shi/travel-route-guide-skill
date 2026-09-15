#!/usr/bin/env python3
"""Small-area OSM roads/coastlines. No tiles; one bounded request; no publishing."""
import argparse,json,ssl,sys,urllib.request,urllib.parse,urllib.error
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--bbox',required=True,help='west,south,east,north WGS84');p.add_argument('--out',type=Path,required=True);a=p.parse_args();w,s,e,n=map(float,a.bbox.split(','))
    if not (-180<=w<e<=180 and -90<=s<n<=90 and e-w<=.8 and n-s<=.8):p.error('Use a valid small bounding box (each span <= 0.8 degree)')
    query=f'[out:json][timeout:40];(way[highway~"^(primary|secondary|tertiary|residential|pedestrian|footway)$"]({s},{w},{n},{e});way[natural=coastline]({s},{w},{n},{e}););out geom;'
    ctx=ssl.create_default_context()
    # macOS system CA bundle is preferable when the Python installation has no CA store.
    if Path('/etc/ssl/cert.pem').is_file():ctx=ssl.create_default_context(cafile='/etc/ssl/cert.pem')
    req=urllib.request.Request('https://overpass-api.de/api/interpreter',data=urllib.parse.urlencode({'data':query}).encode(),headers={'User-Agent':'TravelRouteGuide/1.0 (small-area offline itinerary)','Content-Type':'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req,context=ctx,timeout=55) as r:result=json.load(r)
    if result.get('remark'):raise RuntimeError('Overpass reported incomplete/error response: '+result['remark'])
    features=[]
    for row in result.get('elements',[]):
        cs=[[p['lon'],p['lat']] for p in row.get('geometry',[])];tags=row.get('tags',{})
        if len(cs)<2:continue
        features.append({'type':'Feature','properties':{'kind':'coast' if tags.get('natural')=='coastline' else 'road','name':tags.get('name',''),'osm_id':row['id']},'geometry':{'type':'LineString','coordinates':cs}})
    if not features:raise RuntimeError('No geographic features returned; do not present an empty basemap as complete')
    data={'type':'FeatureCollection','features':features,'source':'https://www.openstreetmap.org/copyright','attribution':'© OpenStreetMap contributors / ODbL'}
    a.out.parent.mkdir(parents=True,exist_ok=True);temp=a.out.with_suffix(a.out.suffix+'.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')));temp.replace(a.out);print(f'{len(features)} geographic features saved to {a.out}')
if __name__=='__main__':
    try:main()
    except (urllib.error.URLError,TimeoutError,RuntimeError) as e:
        print('Map data unavailable; existing output was preserved. '+str(e),file=sys.stderr);sys.exit(2)
