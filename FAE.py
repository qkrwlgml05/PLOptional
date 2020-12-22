import click
import sys
from nltk import Tree

def parserTree (sentence):
    if '{' not in sentence and '}' not in sentence:
        return sentence
    sentence_1 = sentence.replace('{', '(').replace('}', ')')
    new_sen = ""
    sen_list = sentence_1.split(' ')
    for s in sen_list:
        if '(' in s:
            new_sen += s + ' '
        else:
            new_sen += '(' + s + ')'

    t = Tree.fromstring(sentence_1)
    return t

class FAE:
    def __init__(self):
        return

    def getType(self):
        return 'FAE'

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
        elif t.label() == 'fun':
            index = 0
            param = ''
            body = ''
            for c in t:
                if index == 0:
                    index += 1
                    param = self.parser(c.label())
                    continue
                body = self.parser(c)
            return FUN(param, body)
        elif t.label() == '':
            child_list = []
            for c in t:
                child_list.append(self.parser(c))
            return APP(child_list[0], child_list[1])
        else:
            child_list = [self.parser(t.label())]
            for c in t:
                child_list.append(self.parser(c))
            return APP(child_list[0], child_list[1])


class NUM(FAE):
    def __init__(self, val):
        self.val = int(val)
        return

    def getType(self):
        return 'NUM'

    def getStr(self):
        return '(num ' + str(self.val) + ')'

    def interp(self, ds):
        return numV(self.val)

class ID(FAE):
    def __init__(self, val):
        self.id = val
        return

    def getType(self):
        return 'ID'

    def getStr(self):
        return '(id \'' + self.id + ')'

    def interp(self, ds):
        return strict(lookup(self.id, ds))

class ADD(FAE):
    lhs = FAE()
    rhs = FAE()

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        return

    def getType(self):
        return 'ADD'

    def getStr(self):
        return '(add ' + self.lhs.getStr() + ' ' + self.rhs.getStr() + ')'

    def interp(self, ds):
        return numV(strict(self.lhs.interp(ds)).val + strict(self.rhs.interp(ds)).val)

class SUB(FAE):
    lhs = FAE()
    rhs = FAE()

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        return

    def getType(self):
        return 'SUB'

    def getStr(self):
        return '(sub ' + self.lhs.getStr() + ' ' + self.rhs.getStr() + ')'

    def interp(self, ds):
        return numV(strict(self.lhs.interp(ds)).val - strict(self.rhs.interp(ds)).val)

class FUN(FAE):
    param = ''
    body = FAE()

    def __init__(self, p, b):
        self.param = p
        self.body = b
        return

    def getType(self):
        return 'FUN'

    def getStr(self):
        return '(fun \'' + self.param.id + ' ' + self.body.getStr() + ')'

    def interp(self, ds):
        return closureV(self.param.id, self.body, ds)

class APP(FAE):
    ftn = FAE()
    arg = FAE()

    def __init__(self, f, a):
        self.ftn = f
        self.arg = a
        return

    def getType(self):
        return 'APP'

    def getStr(self):
        return '(app ' + self.ftn.getStr() + ' ' + self.arg.getStr() + ')'

    def interp(self, ds):
        ftn = self.ftn.interp(ds)
        # arg = self.arg.interp(ds)
        arg = exprV(self.arg, ds, box())
        return ftn.body.interp(aSub(ftn.param, arg, ftn.ds))

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
    value = 0
    saved = DefrdSub()

    def __init__(self, n, v, s):
        self.name = n
        self.value = v
        self.saved = s
        return

    def getType(self):
        return 'aSub'

    def getStr(self):
        return '(aSub ' + self.name + ' ' + self.value.getStr() + ' ' + self.saved.getStr() + ')'

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

class FAEValue:
    def __init__(self):
        return

class numV(FAEValue):
    val = 0
    def __init__(self, num):
        self.val = num
        return

    def getType(self):
        return 'numV'

    def getStr(self):
        return '(num ' + str(self.val) + ')'

    def interp(self):
        return self

class closureV(FAEValue):
    param = ''
    body = FAE()
    ds = DefrdSub()
    def __init__(self, p, b, d):
        self.param = p
        self.body = b
        self.ds = d
        return

    def getType(self):
        return 'closureV'

    def getStr(self):
        return '(closureV \'' + self.param + ' ' + self.body.getStr() + ' ' + self.ds.getStr() + ')'

class exprV(FAEValue):
    expr = FAE()
    ds = DefrdSub()
    value = box()

    def __init__(self, e, d, v):
        self.expr = e
        self.ds = d
        self.value = v
        return

    def getType(self):
        return 'exprV'

    def getStr(self):
        return '(exprV ' + self.expr.getStr() + ' ' + self.ds.getStr() + ' ' + self.value.getStr() + ')'

def subst(fae, idtf, val):
    if fae.getType() == 'NUM':
        return fae
    elif fae.getType() == 'ADD':
        return ADD(subst(fae.lhs, idtf, val), subst(fae.rhs, idtf, val))
    elif fae.getType() == 'SUB':
        return SUB(subst(fae.lhs, idtf, val), subst(fae.rhs, idtf, val))
    elif fae.getType() == 'ID':
        if fae.id == idtf.id:
            return val
        else:
            return fae
    elif fae.getType() == 'APP':
        return APP(subst(fae.ftn, idtf, val), subst(fae.arg, idtf, val))
    elif fae.getType() == 'FUN':
        if fae.param.id == idtf:
            return fae
        else:
            return FUN(fae.param, subst(fae.body, idtf, val))

def lookup(name, ds):
    if ds.getType() == 'mtSub':
        print('lookup free identifier')
        exit(-1)
    elif ds.getType() == 'aSub':
        if ds.name == name:
            return ds.value
        else:
            return lookup(name, ds.saved)

def strict(v):
    if v.getType() == 'exprV':
        if not v.value.unbox():
            val = strict(v.expr.interp(v.ds))
            v.value.value = val
            return val
        else:
            return v.value.unbox()
    else:
        return v

@click.command()
@click.option('--parser', '-p', help='parsed arithmetic')
def main (parser):
    t = parserTree(sentence=sys.argv[-1])
    ae = FAE()
    s = ae.parser(t)
    print(s.getStr())

def AEparser2 ():
    t = parserTree(sentence=sys.argv[-1])
    ae = FAE()
    s = ae.parser(t)
    mt = mtSub()
    print(s.interp(mt).getStr())

if len(sys.argv) == 2 and sys.argv[-1] != '--help':
    AEparser2()
elif __name__ == "__main__":
    main()
else:
    print("--Input format--")
    print("\tpython FAE.py 'input text'")
    print("\tor")
    print("\tpython FAE.py -p 'input text'")

