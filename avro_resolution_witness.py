import argparse, json, pathlib, sys

def need(ok, message):
    if not ok: raise ValueError(message)

def integer(x, label, minimum=None):
    need(type(x) is int and abs(x) <= 10**15, label + " must be a bounded integer")
    need(minimum is None or x >= minimum, label + " below minimum")
    return x

def ident(x):
    need(isinstance(x,str) and 0 < len(x) <= 128, "expected nonempty identifier <=128 characters")
    return x

def fields(x, required, optional=()):
    need(type(x) is dict and set(required)<=set(x)<=set(required)|set(optional), "invalid object fields")

def pairs(items):
    out={}
    for k,v in items:
        need(k not in out, "duplicate JSON key")
        out[k]=v
    return out

def load(path):
    with pathlib.Path(path).open('rb') as handle: raw=handle.read(1048577)
    need(len(raw)<=1048576,"input exceeds 1 MiB")
    def bad(x): raise ValueError("nonfinite JSON number")
    return json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=bad)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',help='UTF-8 JSON input; read only')
    args=parser.parse_args()
    try:
        result=analyze(load(args.input))
        print(json.dumps(result,ensure_ascii=True,indent=2,allow_nan=False))
        return 1 if result.get('findings') else 0
    except (ValueError,OSError,RecursionError,OverflowError) as exc:
        print(str(exc),file=sys.stderr);return 2

PRIMITIVES={'null','boolean','int','long','float','double','bytes','string'}
PROMOTIONS={'int':{'long','float','double'},'long':{'float','double'},'float':{'double'},'string':{'bytes'},'bytes':{'string'}}

def kind(s):return 'union' if type(s) is list else s['type']

def default_matches(s,value):
    k=kind(s)
    if k=='union':return any(default_matches(b,value) for b in s)
    if k in ('record','array','map'):raise ValueError('composite defaults are outside this alpha scope')
    if k=='null':return value is None
    if k=='boolean':return type(value) is bool
    if k in ('int','long'):return type(value) is int and -(2**(31 if k=='int' else 63))<=value<2**(31 if k=='int' else 63)
    if k in ('float','double'):return type(value) in (int,float) and abs(value)<=1.7976931348623157e308
    if k=='enum':return value in s['symbols']
    if k=='string':return type(value) is str
    if k in ('bytes','fixed'):return type(value) is str and all(ord(c)<=255 for c in value) and (k=='bytes' or len(value)==s['size'])
    return False

def validate(schema):
    import re
    names=set();nodes=0
    def name(value):
        need(type(value) is str and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',value) is not None,'only unqualified Avro names are supported')
        return value
    def visit(s,depth=0):
        nonlocal nodes
        nodes+=1;need(nodes<=300 and depth<=24,'schema node/depth bound exceeded')
        if type(s) is str:
            need(s in PRIMITIVES,'named references are not supported');return {'type':s}
        if type(s) is list:
            need(0<len(s)<=16 and all(type(b) is not list for b in s),'invalid/bounded union')
            branches=[visit(b,depth+1) for b in s]
            keys=[(kind(b),b.get('name')) if kind(b) in ('record','enum','fixed') else (kind(b),None) for b in branches]
            need(len(set(keys))==len(keys),'duplicate union branch');return branches
        need(type(s) is dict and type(s.get('type')) is str,'schema must be a primitive, object or union')
        k=s['type'];out={'type':k}
        attrs={'record':{'name','fields'},'enum':{'name','symbols'},'fixed':{'name','size'},'array':{'items'},'map':{'values'}}
        need(k in PRIMITIVES or k in attrs,'unsupported schema kind')
        fields(s,['type']+sorted(attrs.get(k,set())),['doc']+(['default'] if k=='enum' else []))
        if 'doc' in s:need(type(s['doc']) is str,'doc must be text')
        if k in ('record','enum','fixed'):
            out['name']=name(s['name']);need(out['name'] not in names,'duplicate named definition');names.add(out['name'])
        if k=='record':
            need(type(s['fields']) is list and len(s['fields'])<=100,'fields must be a list <=100')
            fs=[];seen=set()
            for field in s['fields']:
                fields(field,['name','type'],['doc','default','order'])
                fn=name(field['name']);need(fn not in seen,'duplicate field');seen.add(fn)
                if 'doc' in field:need(type(field['doc']) is str,'field doc must be text')
                if 'order' in field:need(field['order'] in ('ascending','descending','ignore'),'invalid order')
                f={'name':fn,'type':visit(field['type'],depth+1)}
                if 'default' in field:
                    need(default_matches(f['type'],field['default']),'invalid field default');f['default']=field['default']
                fs.append(f)
            out['fields']=fs
        elif k=='enum':
            need(type(s['symbols']) is list and 0<len(s['symbols'])<=100,'symbols must be a nonempty list <=100')
            out['symbols']=[name(x) for x in s['symbols']];need(len(set(out['symbols']))==len(out['symbols']),'duplicate enum symbol')
            if 'default' in s:need(s['default'] in out['symbols'],'invalid enum default');out['default']=s['default']
        elif k=='fixed':out['size']=integer(s['size'],'fixed size',1)
        elif k=='array':out['items']=visit(s['items'],depth+1)
        elif k=='map':out['values']=visit(s['values'],depth+1)
        return out
    return visit(schema)

def matches(w,r):
    a,b=kind(w),kind(r)
    if a=='union' or b=='union':return True
    if a!=b:return b in PROMOTIONS.get(a,set())
    if a in ('record','enum'):return w['name']==r['name']
    if a=='fixed':return w['name']==r['name'] and w['size']==r['size']
    if a in ('array','map'):
        child='items' if a=='array' else 'values';return matches(w[child],r[child])
    return True

def analyze(data):
    fields(data,['writer','reader']);writer=validate(data['writer']);reader=validate(data['reader']);trace=[];errors=[]
    def resolve(w,r,path):
        a,b=kind(w),kind(r)
        if a=='union':
            for i,branch in enumerate(w):resolve(branch,r,path+'/writer_union/'+str(i))
            return
        if b=='union':
            selected=next((i for i,branch in enumerate(r) if matches(w,branch)),None)
            if selected is None:errors.append({'path':path,'reason':'no reader union branch matches'});return
            trace.append({'path':path,'rule':'reader_union','branch':selected});resolve(w,r[selected],path+'/reader_union/'+str(selected));return
        if not matches(w,r):errors.append({'path':path,'reason':'type/name/size mismatch','writer':a,'reader':b});return
        trace.append({'path':path,'rule':'same_type' if a==b else 'promotion','writer':a,'reader':b})
        if a==b=='record':
            wf={f['name']:f for f in w['fields']};rf={f['name']:f for f in r['fields']}
            for name in sorted(set(wf)-set(rf)):trace.append({'path':path+'/'+name,'rule':'writer_field_ignored'})
            for name,f in rf.items():
                if name in wf:resolve(wf[name]['type'],f['type'],path+'/'+name)
                elif 'default' in f:trace.append({'path':path+'/'+name,'rule':'reader_default','value':f['default']})
                else:errors.append({'path':path+'/'+name,'reason':'reader field missing and has no default'})
        elif a==b=='enum':
            for symbol in w['symbols']:
                if symbol not in r['symbols']:
                    if 'default' in r:trace.append({'path':path,'rule':'enum_default','writer_symbol':symbol,'value':r['default']})
                    else:errors.append({'path':path,'reason':'writer enum symbol missing','symbol':symbol})
        elif a==b and a in ('array','map'):
            child='items' if a=='array' else 'values';resolve(w[child],r[child],path+'/'+child)
    resolve(writer,reader,'$')
    return {'compatible_for_all_writer_branches':not errors,'trace':trace,'findings':errors,
            'scope':'unqualified inline schemas; no named references, namespaces, aliases, logical types or composite defaults'}

if __name__=='__main__':sys.exit(main())
