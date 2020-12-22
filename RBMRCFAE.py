import click
import sys
from nltk import Tree

def parserTree (sentence):
    if '{' not in sentence and '}' not in sentence:
        return sentence
    sentence_1 = sentence.replace('{', '(').replace('}', ')').replace('\n', ' ')
    new_sen = ""
    sen_list = sentence_1.split(' ')
    for s in sen_list:
        if '(' in s:
            new_sen += s + ' '
        else:
            new_sen += '(' + s + ')'

    t = Tree.fromstring(sentence_1)
    return t

type_list = {'RBMRCFAE': ['NUM', 'ID', 'ADD', 'SUB', 'FUN', 'APP'],
             'DefrdSub': ['mtSub', 'aSub', 'aRecSub'],
             'RBMRCFAEValue': ['numV', 'closureV']}

### RBMRCFAE
class RBMRCFAE:
    def __init__(self):
        return

    def getType(self):
        return 'RBMRCFAE'

    def parser(self, t):
        child_list = []
        if type(t) is str and t.isnumeric():
            return NUM(int(t))
        elif type(t) is str:
            return ID(t)

        if t.label() == '+':
            for c in t:
                child_list.append(self.parser(c))
            return ADD(child_list[0], child_list[1])
        elif t.label() == '-':
            for c in t:
                child_list.append(self.parser(c))
            return SUB(child_list[0], child_list[1])
        elif t.label() == 'with':
            index = 0
            id = ''
            value = ''
            event = ''
            for c in t:
                if index == 0:
                    index += 1
                    id = self.parser(c.label())
                    for v in c:
                        value = self.parser(v)
                event = self.parser(c)
            return APP(FUN(id, event), value)
        elif t.label() == 'fun' or t.label() == 'refun':
            index = 0
            param = ''
            body = ''
            for c in t:
                if index == 0:
                    index += 1
                    param = self.parser(c.label())
                    continue
                body = self.parser(c)

            if t.label() == 'fun':
                return FUN(param, body)
            else: return REFUN(param, body)
        elif t.label() == '':
            child_list = []
            for c in t:
                child_list.append(self.parser(c))
            return APP(child_list[0], child_list[1])
        elif t.label() == 'if0':
            child_list = []
            for c in t:
                child_list.append(self.parser(c))
            return IF0(child_list[0], child_list[1], child_list[2])
        elif t.label() == 'rec':
            index = 0
            id = ''
            value = ''
            event = ''
            for c in t:
                if index == 0:
                    index += 1
                    id = self.parser(c.label())
                    for v in c:
                        value = self.parser(v)
                event = self.parser(c)
            return REC(id, value, event)
        elif t.label() == 'newbox':
            child_list = []
            for c in t:
                child_list.append(self.parser(c))
            return newbox(child_list[0])
        elif t.label() == 'setbox':
            child_list = []
            for c in t:
                child_list.append(self.parser(c))
            return setbox(child_list[0], child_list[1])
        elif t.label() == 'openbox':
            child_list = []
            for c in t:
                child_list.append(self.parser(c))
            return openbox(child_list[0])
        elif t.label() == 'seqn':
            child_list = []
            for c in t:
                child_list.append(self.parser(c))
            return seqn(child_list[0], child_list[1])
        elif t.label() == 'setvar':
            child_list = []
            for c in t:
                child_list.append(self.parser(c))
            return setvar(child_list[0], child_list[1])
        else:
            child_list = [self.parser(t.label())]
            for c in t:
                child_list.append(self.parser(c))
            return APP(child_list[0], child_list[1])

class NUM(RBMRCFAE):
    def __init__(self, val):
        self.val = int(val)
        return

    def getType(self):
        return 'NUM'

    def getStr(self):
        return '(num ' + str(self.val) + ')'

    def interp(self, ds, st):
        return vs(numV(self.val), st)

class ID(RBMRCFAE):
    def __init__(self, val):
        self.id = val
        return

    def getType(self):
        return 'ID'

    def getStr(self):
        return '(id \'' + self.id + ')'

    def interp(self, ds, st):
        return vs(storeLK(lookup(self.id, ds), st), st)

class ADD(RBMRCFAE):
    lhs = RBMRCFAE()
    rhs = RBMRCFAE()

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        return

    def getType(self):
        return 'ADD'

    def getStr(self):
        return '(add ' + self.lhs.getStr() + ' ' + self.rhs.getStr() + ')'

    def interp(self, ds, st):
        lhs = self.lhs.interp(ds, st)
        rhs = self.rhs.interp(ds, lhs.store)
        return vs(numV(lhs.value.val + rhs.value.val), rhs.store)

class SUB(RBMRCFAE):
    lhs = RBMRCFAE()
    rhs = RBMRCFAE()

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        return

    def getType(self):
        return 'SUB'

    def getStr(self):
        return '(sub ' + self.lhs.getStr() + ' ' + self.rhs.getStr() + ')'

    def interp(self, ds, st):
        lhs = self.lhs.interp(ds, st)
        rhs = self.rhs.interp(ds, lhs.store)
        return vs(numV(lhs.value.val - rhs.value.val), rhs.store)

class FUN(RBMRCFAE):
    param = ''
    body = RBMRCFAE()

    def __init__(self, p, b):
        self.param = p
        self.body = b
        return

    def getType(self):
        return 'FUN'

    def getStr(self):
        return '(fun \'' + self.param.id + ' ' + self.body.getStr() + ')'

    def interp(self, ds, st):
        return vs(closureV(self.param.id, self.body, ds), st)

class REFUN(RBMRCFAE):
    param = ''
    body = RBMRCFAE()

    def __init__(self, p, b):
        self.param = p
        self.body = b
        return

    def getType(self):
        return 'REFUN'

    def getStr(self):
        return '(refun \'' + self.param.id + ' ' + self.body.getStr() + ')'

    def interp(self, ds, st):
        return vs(refclosV(self.param.id, self.body, ds), st)

class APP(RBMRCFAE):
    ftn = RBMRCFAE()
    arg = RBMRCFAE()

    def __init__(self, f, a):
        self.ftn = f
        self.arg = a
        return

    def getType(self):
        return 'APP'

    def getStr(self):
        return '(app ' + self.ftn.getStr() + ' ' + self.arg.getStr() + ')'

    def interp(self, ds, st):
        ftn = self.ftn.interp(ds, st)
        if ftn.value.getType() == 'closureV':
            arg = self.arg.interp(ds, ftn.store)
            address = malloc(ftn.store)
            return ftn.value.body.interp(aSub(ftn.value.param, address, ftn.value.ds), aSto(address, arg.value, arg.store))
        elif ftn.value.getType() == 'refclosV':
            address = lookup(self.arg.id, ds)
            return ftn.value.body.interp(aSub(ftn.value.param, address, ftn.value.ds), ftn.store)
        else:
            print('trying to apply a number')
            exit(-1)

class IF0 (RBMRCFAE):
    testE = RBMRCFAE()
    thenE = RBMRCFAE()
    elseE = RBMRCFAE()

    def __init__(self, te, th, el):
        self.testE = te
        self.thenE = th
        self.elseE = el
        return

    def getType(self):
        return 'IF0'

    def getStr(self):
        return '(if0 ' + self.testE.getStr() + ' ' + self.thenE.getStr() + ' ' + self.elseE.getStr() + ')'

    def interp(self, ds, st):
        test = self.testE.interp(ds, st)

        if test.value.val == 0:
            return self.thenE.interp(ds, test.store)
        else:
            return self.elseE.interp(ds, test.store)

class REC(RBMRCFAE):
    name = ''
    namedE = RBMRCFAE()
    fst = RBMRCFAE()

    def __init__(self, n, nd, f):
        self.name = n
        self.namedE = nd
        self.fst = f
        return

    def getType(self):
        return 'REC'

    def getStr(self):
        return '(rec \'' + self.name.id + ' ' + self.namedE.getStr() + ' ' + self.fst.getStr() + ')'

    def interp(self, ds, st):
        value_holder = box(numV(777))
        new_addr = malloc(st)
        new_ds = aSub(self.name.id, new_addr, ds)
        new_st = aRecSto(new_addr, value_holder, st)
        value_holder.value = self.namedE.interp(new_ds, new_st).value
        return self.fst.interp(new_ds, new_st)

class newbox(RBMRCFAE):
    val = RBMRCFAE()
    def __init__(self, v):
        self.val = v
        return

    def getType(self):
        return 'newbox'

    def getStr(self):
        return '(newbox ' + self.val.getStr() + ')'

    def interp(self, ds, st):
        val = self.val.interp(ds, st)
        a = malloc(st)
        return vs(boxV(a), aSto(a, vs(boxV(a), aSto(a, val.value, val.store))))

class setbox(RBMRCFAE):
    box = RBMRCFAE()
    val = RBMRCFAE()

    def __init__(self, b, v):
        self.box = b
        self.val = v
        return

    def getType(self):
        return 'setbox'

    def getStr(self):
        return '(setbox ' + self.box.getStr() + ' ' + self.val.getStr() + ')'

    def interp(self, ds, st):
        box = self.box.interp(ds, st)
        val = self.val.interp(ds, box.store)

        return vs(val.value, aSto(box.value.address, val.value, val.store))

class openbox(RBMRCFAE):
    box = RBMRCFAE()

    def __init__(self, b):
        self.box = b
        return

    def getType(self):
        return 'openbox'

    def getStr(self):
        return '(openbox ' + self.box.getStr() + ')'

    def interp(self, ds, st):
        val = self.box.interp(ds, st)
        return vs(storeLK(val.value.address, val.store), val.store)

class seqn(RBMRCFAE):
    fexp = RBMRCFAE()
    sexp = RBMRCFAE()

    def __init__(self, f, s):
        self.fexp = f
        self.sexp = s
        return

    def getType(self):
        return 'seqn'

    def getStr(self):
        return '(seqn ' + self.fexp.getStr() + ' ' + self.sexp.getStr() + ')'

    def interp(self, ds, st):
        first = self.fexp.interp(ds, st)
        second = self.sexp.interp(ds, first.store)
        return vs(second.value, second.store)

class setvar(RBMRCFAE):
    id = ''
    val = RBMRCFAE()

    def __init__(self, i, v):
        self.id = i
        self.val = v
        return

    def getType(self):
        return 'setvar'

    def getStr(self):
        return '(setvar \'' + self.id.id + ' ' + self.val.getStr() + ')'

    def interp(self, ds, st):
        a = lookup(self.id.id, ds)
        val = self.val.interp(ds, st)
        return vs(val.value, aSto(a, val.value, val.store))

### box
class box:
    value = False

    def __init__(self, v=False):
        self.value = v
        return

    def getType(self):
        return 'box'

    def unbox(self):
        return self.value

    def getStr(self):
        if not self.value:
            return '(box #f)'
        else:
            return '(box ' + self.value.getStr() + ')'

### DefrdSub
class DefrdSub:
    def __init__(self):
        return

class mtSub(DefrdSub):
    def __init__(self):
        return

    def getType(self):
        return 'mtSub'

    def getStr(self):
        return '(mtSub)'

class aSub(DefrdSub):
    name = ''
    address = 0
    saved = DefrdSub()

    def __init__(self, n, v, s):
        self.name = n
        self.address = v
        self.saved = s
        return

    def getType(self):
        return 'aSub'

    def getStr(self):
        return '(aSub \'' + self.name + ' ' + str(self.address) + ' ' + self.saved.getStr() + ')'

### RBMRCFAEValue
class RBMRCFAEValue:
    def __init__(self):
        return

class numV(RBMRCFAEValue):
    val = 0
    def __init__(self, num):
        self.val = num
        return

    def getType(self):
        return 'numV'

    def getStr(self):
        return '(numV ' + str(self.val) + ')'

    def interp(self):
        return self

class closureV(RBMRCFAEValue):
    param = ''
    body = RBMRCFAE()
    ds = DefrdSub()
    def __init__(self, p, b, d):
        self.param = p
        self.body = b
        self.ds = d
        return

    def getType(self):
        return 'closureV'

    def getStr(self):
        return '(closureV ' + self.param + ' ' + self.body.getStr() + ' ' + self.ds.getStr() + ')'

class refclosV(RBMRCFAEValue):
    param = ''
    body = RBMRCFAE()
    ds = DefrdSub()
    def __init__(self, p, b, d):
        self.param = p
        self.body = b
        self.ds = d
        return

    def getType(self):
        return 'refclosV'

    def getStr(self):
        return '(refclosV \'' + self.param + ' ' + self.body.getStr() + ' ' + self.ds.getStr() + ')'

class boxV(RBMRCFAEValue):
    address = 0
    def __init__(self, a):
        self.address = a
        return

    def getType(self):
        return 'boxV'

    def getStr(self):
        return '(boxV ' + str(self.address) + ')'

### Store
class Store:
    def __init__(self):
        return

    def getType(self):
        return 'Store'

class mtSto(Store):
    def __init__(self):
        return

    def getType(self):
        return 'mtSto'

    def getStr(self):
        return '(mtSto)'

class aSto(Store):
    address = 0
    value = RBMRCFAEValue()
    rest = Store()

    def __init__(self, a, v, r):
        self.address = a
        self.value = v
        self.rest = r
        return

    def getType(self):
        return 'aSto'

    def getStr(self):
        return '(aSto ' + str(self.address) + ' ' + self.value.getStr() + ' ' + self.rest.getStr() + ')'

class aRecSto(Store):
    address = ''
    value = box()
    rest = Store()

    def __init__(self, n, v, d):
        self.address = n
        self.value = v
        self.rest = d
        return

    def getType(self):
        return 'aRecSto'

    def getStr(self):
        return '(aRecSto ' + str(self.address) + ' ' + self.value.value.getStr() + ' ' + self.rest.getStr() + ')'

### Value*Store
class ValueStore:
    def __init__(self):
        return

    def getType(self):
        return 'ValueStore'

class vs (ValueStore):
    value = RBMRCFAEValue()
    store = Store()

    def __init__(self, v, s):
        self.value = v
        self.store = s
        return

    def getType(self):
        return 'v*s'

    def getStr(self):
        return '(v*s ' + self.value.getStr() + ' ' + self.store.getStr() + ')'

### functions
def subst(rbmrcfae, idtf, val):
    if rbmrcfae.getType() == 'NUM':
        return rbmrcfae
    elif rbmrcfae.getType() == 'ADD':
        return ADD(subst(rbmrcfae.lhs, idtf, val), subst(rbmrcfae.rhs, idtf, val))
    elif rbmrcfae.getType() == 'SUB':
        return SUB(subst(rbmrcfae.lhs, idtf, val), subst(rbmrcfae.rhs, idtf, val))
    elif rbmrcfae.getType() == 'ID':
        if rbmrcfae.id == idtf.id:
            return val
        else:
            return rbmrcfae
    elif rbmrcfae.getType() == 'APP':
        return APP(subst(rbmrcfae.ftn, idtf, val), subst(rbmrcfae.arg, idtf, val))
    elif rbmrcfae.getType() == 'FUN':
        if rbmrcfae.param.id == idtf:
            return rbmrcfae
        else:
            return FUN(rbmrcfae.param, subst(rbmrcfae.body, idtf, val))

def lookup(name, ds):
    if ds.getType() == 'mtSub':
        print('lookup free identifier')
        exit(-1)
    elif ds.getType() == 'aSub':
        if ds.name == name:
            return ds.address
        else:
            return lookup(name, ds.saved)

def storeLK(addr, st):
    if st.getType() == 'mtSto':
        print('store-lookup: No value at address')
        exit(-1)
    elif st.getType() == 'aSto':
        if st.address == addr:
            return st.value
        else:
            return storeLK(addr, st.rest)
    elif st.getType() == 'aRecSto':
        if st.address == addr:
            return st.value.unbox()
        else:
            return storeLK(addr, st.rest)

def malloc(st):
    return 1+maxAddr(st)

def maxAddr(st):
    if st.getType() == 'mtSto':
        return 0
    elif st.getType() == 'aSto' or st.getType() == 'aRecSto':
        max = maxAddr(st.rest)
        if st.address > max:
            return st.address
        else:
            return max

@click.command()
@click.option('--parser', '-p', help='parsed arithmetic')
def main (parser):
    t = parserTree(sentence=sys.argv[-1])
    ae = RBMRCFAE()
    s = ae.parser(t)
    print(s.getStr())

def AEparser2 ():
    t = parserTree(sentence=sys.argv[-1])
    ae = RBMRCFAE()
    s = ae.parser(t)
    mtsub = mtSub()
    mtsto = mtSto()
    print(s.interp(mtsub, mtsto).getStr())

if len(sys.argv) == 2 and sys.argv[-1] != '--help':
    AEparser2()
elif __name__ == "__main__":
    main()
else:
    print("--Input format--")
    print("\tpython AE.py 'input text'")
    print("\tor")
    print("\tpython AE.py -p 'input text'")
