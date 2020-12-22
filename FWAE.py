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

class FWAE:
    def __init__(self):
        return

    def getType(self):
        return 'FWAE'

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
            return WITH(id, value, event)
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


class NUM(FWAE):
    def __init__(self, val):
        self.val = int(val)
        return

    def getType(self):
        return 'NUM'

    def getStr(self):
        return '(num ' + str(self.val) + ')'

    def interp(self):
        return self

class ID(FWAE):
    def __init__(self, val):
        self.id = val
        return

    def getType(self):
        return 'ID'

    def getStr(self):
        return '(id \'' + self.id + ')'

    def interp(self):
        print('Free identifier: {}'.format(self.id))
        exit(-1)

class ADD(FWAE):
    lhs = FWAE()
    rhs = FWAE()

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        return

    def getType(self):
        return 'ADD'

    def getStr(self):
        return '(add ' + self.lhs.getStr() + ' ' + self.rhs.getStr() + ')'

    def interp(self):
        return NUM(self.lhs.interp().val + self.rhs.interp().val)

class SUB(FWAE):
    lhs = FWAE()
    rhs = FWAE()

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        return

    def getType(self):
        return 'SUB'

    def getStr(self):
        return '(sub ' + self.lhs.getStr() + ' ' + self.rhs.getStr() + ')'

    def interp(self):
        return NUM(self.lhs.interp().val - self.rhs.interp().val)

class WITH(FWAE):
    id = FWAE()
    value = FWAE()
    event = FWAE()

    def __init__(self, i, v, e):
        self.id = i
        self.value = v
        self.event = e
        return

    def getType(self):
        return 'WITH'

    def getStr(self):
        return '(with \'' + self.id.id + ' ' + self.value.getStr() + ' ' + self.event.getStr() + ')'

    def interp(self):
        return subst(self.event, self.id, self.value.interp()).interp()

class FUN(FWAE):
    param = ''
    body = FWAE()

    def __init__(self, p, b):
        self.param = p
        self.body = b
        return

    def getType(self):
        return 'FUN'

    def getStr(self):
        return '(fun \'' + self.param.id + ' ' + self.body.getStr() + ')'

    def interp(self):
        return self

class APP(FWAE):
    ftn = FWAE()
    arg = FWAE()

    def __init__(self, f, a):
        self.ftn = f
        self.arg = a
        return

    def getType(self):
        return 'APP'

    def getStr(self):
        return '(app ' + self.ftn.getStr() + ' ' + self.arg.getStr() + ')'

    def interp(self):
        ftn = self.ftn.interp()
        return subst(ftn.body, ftn.param, self.arg.interp()).interp()

def subst(fwae, idtf, val):
    if fwae.getType() == 'NUM':
        return fwae
    elif fwae.getType() == 'ADD':
        return ADD(subst(fwae.lhs, idtf, val), subst(fwae.rhs, idtf, val))
    elif fwae.getType() == 'SUB':
        return SUB(subst(fwae.lhs, idtf, val), subst(fwae.rhs, idtf, val))
    elif fwae.getType() == 'WITH':
        if fwae.id.id == idtf:
            return WITH(fwae.id, subst(fwae.value, idtf, val), fwae.event)
        else:
            return WITH(fwae.id, subst(fwae.value, idtf, val), subst(fwae.event, idtf, val))
    elif fwae.getType() == 'ID':
        if fwae.id == idtf.id:
            return val
        else:
            return fwae
    elif fwae.getType() == 'APP':
        return APP(subst(fwae.ftn, idtf, val), subst(fwae.arg, idtf, val))
    elif fwae.getType() == 'FUN':
        if fwae.param.id == idtf:
            return fwae
        else:
            return FUN(fwae.param, subst(fwae.body, idtf, val))

@click.command()
@click.option('--parser', '-p', help='parsed arithmetic')
def main (parser):
    t = parserTree(sentence=sys.argv[-1])
    ae = FWAE()
    s = ae.parser(t)
    print(s.getStr())

def AEparser2 ():
    t = parserTree(sentence=sys.argv[-1])
    ae = FWAE()
    s = ae.parser(t)
    print(s.interp().getStr())

if len(sys.argv) == 2 and sys.argv[-1] != '--help':
    AEparser2()
elif __name__ == "__main__":
    main()
else:
    print("--Input format--")
    print("\tpython FWAE.py 'input text'")
    print("\tor")
    print("\tpython FWAE.py -p 'input text'")

