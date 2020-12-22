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

class WAE:
    def __init__(self):
        return

    def getType(self):
        return 'WAE'

    def parser(self, t):
        child_list = []
        if type(t) is str and t.isnumeric():
            return NUM(int(t))
        elif type(t) is str:
            return ID(t)

        if t.label() == '+':
            for c in t:
                if type(c) is str and c.isnumeric():
                    child_list.append(NUM(int(c)))
                elif type(c) is str:
                    child_list.append(ID(c))
                else:
                    child_list.append(self.parser(c))
            return ADD(child_list[0], child_list[1])
        elif t.label() == '-':
            for c in t:
                if type(c) is str and c.isnumeric():
                    child_list.append(NUM(int(c)))
                elif type(c) is str:
                    child_list.append(ID(c))
                else:
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
                if type(c) is str and c.isnumeric():
                    event = NUM(int(c))
                elif type(c) is str:
                    event = ID(c)
                else:
                    event = self.parser(c)
            return WITH(id, value, event)


class NUM(WAE):
    def __init__(self, val):
        self.val = int(val)
        return

    def getType(self):
        return 'NUM'

    def getStr(self):
        return '(num ' + str(self.val) + ')'

    def interp(self):
        return self.val

class ID(WAE):
    def __init__(self, val):
        self.id = val
        return

    def getType(self):
        return 'ID'

    def getStr(self):
        return '(id \'' + self.id + ')'

    def interp(self):
        print('Free identifier')
        exit(-1)

class ADD(WAE):
    lhs = WAE()
    rhs = WAE()

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        return

    def getType(self):
        return 'ADD'

    def getStr(self):
        return '(add ' + self.lhs.getStr() + ' ' + self.rhs.getStr() + ')'

    def interp(self):
        return self.lhs.interp() + self.rhs.interp()

class SUB(WAE):
    lhs = WAE()
    rhs = WAE()

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        return

    def getType(self):
        return 'SUB'

    def getStr(self):
        return '(sub ' + self.lhs.getStr() + ' ' + self.rhs.getStr() + ')'

    def interp(self):
        return self.lhs.interp() - self.rhs.interp()

class WITH(WAE):
    id = WAE()
    value = WAE()
    event = WAE()

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

def subst(wae, idtf, val):
    if wae.getType() == 'NUM':
        return wae
    elif wae.getType() == 'ADD':
        return ADD(subst(wae.lhs, idtf, val), subst(wae.rhs, idtf, val))
    elif wae.getType() == 'SUB':
        return SUB(subst(wae.lhs, idtf, val), subst(wae.rhs, idtf, val))
    elif wae.getType() == 'WITH':
        if wae.id == idtf.id:
            return WITH(wae.id, subst(wae.value, idtf, val), wae.event)
        else:
            return WITH(wae.id, subst(wae.value, idtf, val), subst(wae.event, idtf, val))
    elif wae.getType() == 'ID':
        if wae.id == idtf:
            return NUM(val)
        else:
            return wae

@click.command()
@click.option('--parser', '-p', help='parsed arithmetic')
def main (parser):
    t = parserTree(sentence=sys.argv[-1])
    ae = WAE()
    s = ae.parser(t)
    print(s.getStr())

def AEparser2 ():
    t = parserTree(sentence=sys.argv[-1])
    ae = WAE()
    s = ae.parser(t)
    print(s.interp())

if len(sys.argv) == 2 and sys.argv[-1] != '--help':
    AEparser2()
elif __name__ == "__main__":
    main()
else:
    print("--Input format--")
    print("\tpython WAE.py 'input text'")
    print("\tor")
    print("\tpython WAE.py -p 'input text'")

