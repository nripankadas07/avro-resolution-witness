import unittest
from avro_resolution_witness import analyze,validate,PRIMITIVES

def record(fields):return {'type':'record','name':'Event','fields':fields}
def resolve(w,r):return analyze({'writer':w,'reader':r})

class ResolutionTests(unittest.TestCase):
    def test_primitive_promotion_truth_table(self):
        allowed={('int','long'),('int','float'),('int','double'),('long','float'),('long','double'),('float','double'),('string','bytes'),('bytes','string')}
        for w in PRIMITIVES:
            for r in PRIMITIVES:self.assertEqual(resolve(w,r)['compatible_for_all_writer_branches'],w==r or (w,r) in allowed)
    def test_record_default_ignore_and_field_order(self):
        w=record([{'name':'extra','type':'int'},{'name':'x','type':'int'}]);r=record([{'name':'x','type':'long'},{'name':'new','type':['null','string'],'default':None}])
        out=resolve(w,r);self.assertFalse(out['findings']);self.assertIn('reader_default',[x['rule'] for x in out['trace']])
        self.assertTrue(resolve(w,record([{'name':'y','type':'string'}]))['findings'])
    def test_all_writer_branches_and_first_reader_match(self):
        self.assertFalse(resolve(['int','string'],'long')['compatible_for_all_writer_branches'])
        r=resolve('int',['double','long']);self.assertEqual(r['trace'][0]['branch'],0)
        # The first matching record is selected even when a required nested field makes resolution fail.
        w=record([]);r=[record([{'name':'x','type':'int'}]),'string'];self.assertTrue(resolve(w,r)['findings'])
    def test_enum_fallback_fixed_array_and_map(self):
        e=lambda symbols,**kw:dict(type='enum',name='Colour',symbols=symbols,**kw)
        self.assertFalse(resolve(e(['A','B']),e(['A'],default='A'))['findings']);self.assertTrue(resolve(e(['B']),e(['A']))['findings'])
        self.assertTrue(resolve(dict(type='fixed',name='F',size=2),dict(type='fixed',name='F',size=3))['findings'])
        for k,child in [('array','items'),('map','values')]:self.assertFalse(resolve({'type':k,child:'int'},{'type':k,child:'double'})['findings'])
    def test_union_default_one_matching_branch(self):
        self.assertTrue(validate(record([dict(name='x',type=['null','string'],default='yes')])) )
    def test_invalid_or_unsupported(self):
        cases=['Ref',{'type':'int','logicalType':'date'},{'type':'record','name':'n.E','fields':[]},['int','int'],record([dict(name='x',type='int',default=True)]),record([dict(name='x',type={'type':'array','items':'int'},default=[])])]
        for schema in cases:
            with self.assertRaises(ValueError):validate(schema)

if __name__=='__main__':unittest.main()
