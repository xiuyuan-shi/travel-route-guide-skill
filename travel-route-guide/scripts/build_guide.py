#!/usr/bin/env python3
"""Validate structured travel data and build one offline mobile HTML. No publishing."""
import argparse, html, json, math, re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

def require(ok, message):
    if not ok: raise ValueError(message)
def url(value):
    require(isinstance(value,str) and urlparse(value).scheme in ('http','https') and bool(urlparse(value).netloc), 'Links must be absolute http/https URLs')
def coord(x,y):
    require(all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in (x,y)) and -180<=x<=180 and -90<=y<=90, 'Invalid WGS84 coordinates')
def nonempty(value, path):
    require(isinstance(value,str) and value.strip(),f'{path} required')
def text_fields(item, fields, path):
    for field in fields: nonempty(item.get(field),f'{path}.{field}')
def validate(d):
    t=d['trip'];days=d['days'];places=d['places'];legs=d.get('legs',{})
    for k in ('origin','destination'):require(isinstance(t.get(k),str) and t[k].strip(),f'trip.{k} required')
    require(isinstance(t['duration'],int) and not isinstance(t['duration'],bool) and t['duration']>0 and t['duration']==len(days),'duration must equal number of days')
    require(bool(places),'At least one mapped place required')
    if t.get('share_url'):url(t['share_url'])
    for k,p in places.items():
        require(bool(p.get('name')),f'{k}: name required');coord(p['lon'],p['lat'])
        require(p.get('kind','spot') in ('spot','food','hotel','station'),f'{k}: unknown place kind')
        if p.get('source_url'):url(p['source_url'])
    for k,l in legs.items():
        require(l['from'] in places and l['to'] in places,f'{k}: missing endpoint')
        require(l['mode'] in ('walk','transit','drive') and l['status'] in ('schematic','routed'),f'{k}: invalid mode/status')
        if l['status']=='routed':
            geo=l.get('geometry',{});require(geo.get('type')=='LineString' and len(geo.get('coordinates',[]))>=2,f'{k}: routed leg needs LineString')
            for a,b in geo['coordinates']:coord(a,b)
        else:require(not l.get('geometry'),f'{k}: schematic must not claim route geometry')
    for i,day in enumerate(days):
        require(bool(day.get('title')) and bool(day.get('stops')),f'Day {i+1}: title/stops required')
        for s in day['stops']:
            require(all(isinstance(s.get(k),str) for k in ('time','title','description')),f'Day {i+1}: invalid stop')
            if s.get('place_id'):require(s['place_id'] in places,f'Day {i+1}: unknown stop place')
        for key in day.get('leg_ids',[]):require(key in legs,f'Day {i+1}: missing leg {key}')
    for i,x in enumerate(d.get('lodging',[])):
        text_fields(x,('place_id','label','price','reason','caveat'),f'lodging[{i}]')
        require(x['place_id'] in places and places[x['place_id']].get('kind')=='hotel',f'lodging[{i}]: place_id must reference a hotel')
    budget=d.get('budget')
    if budget:
        text_fields(budget,('basis','total_estimate','reserve_note'),'budget')
        require(isinstance(budget.get('items'),list) and budget['items'],'budget.items required')
        for i,x in enumerate(budget['items']):text_fields(x,('label','amount','note'),f'budget.items[{i}]')
    for i,x in enumerate(d.get('food_quick',[])):
        text_fields(x,('place_id','when','order','budget','fallback'),f'food_quick[{i}]')
        require(x['place_id'] in places and places[x['place_id']].get('kind')=='food',f'food_quick[{i}]: place_id must reference food')
    for i,x in enumerate(d.get('checklist',[])):
        nonempty(x.get('category'),f'checklist[{i}].category')
        require(isinstance(x.get('items'),list) and x['items'],f'checklist[{i}].items required')
        for j,item in enumerate(x['items']):nonempty(item,f'checklist[{i}].items[{j}]')
    for name,fields in (('pitfalls',('title','advice')),('emergencies',('scenario','action'))):
        for i,x in enumerate(d.get(name,[])):text_fields(x,fields,f'{name}[{i}]')
    weather=d.get('weather')
    if weather:
        require(weather.get('provider')=='open-meteo','weather.provider must be open-meteo')
        coord(weather.get('lon'),weather.get('lat'));nonempty(weather.get('timezone'),'weather.timezone')
        try:start=date.fromisoformat(weather['start_date']);end=date.fromisoformat(weather['end_date'])
        except (KeyError,TypeError,ValueError):raise ValueError('weather start_date/end_date must be YYYY-MM-DD')
        require(start<=end,'weather date range invalid')
        if weather.get('official_url'):url(weather['official_url'])
    for s in d.get('sources',[]):url(s['url'])
    base=d.get('basemap')
    if base:require(base.get('type')=='FeatureCollection' and isinstance(base.get('features'),list),'basemap must be FeatureCollection')
    return d

def main():
    a=argparse.ArgumentParser();a.add_argument('input',type=Path);a.add_argument('--out',type=Path,required=True);args=a.parse_args()
    d=json.loads(args.input.read_text(encoding='utf8'))
    if d.get('basemap_file'):
        d['basemap']=json.loads((args.input.parent/d['basemap_file']).read_text(encoding='utf8'))
    validate(d);assets=Path(__file__).resolve().parents[1]/'assets'
    payload=json.dumps(d,ensure_ascii=False,separators=(',',':')).replace('&','\\u0026').replace('<','\\u003c').replace('>','\\u003e').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    e=html.escape
    fallback=''.join('<h2>'+e(x['title'])+'</h2>'+''.join('<p>'+e(s['time']+' '+s['title']+'：'+s['description'])+'</p>' for s in x['stops']) for x in d['days'])
    values={'TITLE':e(d['trip'].get('title',d['trip']['destination']+'旅行攻略')),'FALLBACK':fallback,'DATA':payload,'CSS':(assets/'leaflet.css').read_text(),'JS':re.sub(r'//# sourceMappingURL=.*','',(assets/'leaflet.js').read_text())}
    text=(assets/'mobile.html').read_text()
    text=re.sub(r'@@(TITLE|FALLBACK|DATA|CSS|JS)@@',lambda m:values[m[1]],text)
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(text,encoding='utf8')
    print(json.dumps({'output':str(args.out.resolve()),'days':len(d['days']),'places':len(d['places']),'bytes':len(text.encode()),'basemap':bool(d.get('basemap',{}).get('features'))},ensure_ascii=False))
if __name__=='__main__':main()
