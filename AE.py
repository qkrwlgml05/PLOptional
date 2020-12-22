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

class AE:
    def __init__(self):
        return

    def parser(self, t):
        child_list = []
        if t.label() == '+':
            for c in t:
                if type(c) is str:
                    child_list.append(NUM(int(c)))
                else:
                    child_list.append(self.parser(c))
            return ADD(child_list[0], child_list[1])
        elif t.label() == '-':
            for c in t:
                if type(c) is str:
                    child_list.append(NUM(int(c)))
                else:
                    child_list.append(self.parser(c))
            return SUB(child_list[0], child_list[1])

class NUM(AE):
    def __init__(self, val):
        self.val = int(val)
        return

    def getStr(self):
        return '(num ' + str(self.val) + ')'

    def interp(self):
        return self.val

class ADD(AE):
    lhs = AE()
    rhs = AE()

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        return

    def getStr(self):
        return '(add ' + self.lhs.getStr() + ' ' + self.rhs.getStr() + ')'

    def interp(self):
        return self.lhs.interp() + self.rhs.interp()

class SUB(AE):
    lhs = AE()
    rhs = AE()

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        return

    def getStr(self):
        return '(sub ' + self.lhs.getStr() + ' ' + self.rhs.getStr() + ')'

    def interp(self):
        return self.lhs.interp() - self.rhs.interp()

@click.command()
@click.option('--parser', '-p', help='parsed arithmetic')
def main (parser):
    t = parserTree(sentence=sys.argv[-1])
    ae = AE()
    s = ae.parser(t)
    print(s.getStr())

def AEparser2 ():
    t = parserTree(sentence=sys.argv[-1])
    ae = AE()
    s = ae.parser(t)
    print(s.interp())

if len(sys.argv) == 2 and sys.argv[-1] != '--help':
    AEparser2()
elif __name__ == "__main__":
    main()
else:
    print("--Input format--")
    print("\tpython AE.py 'input text'")
    print("\tor")
    print("\tpython AE.py -p 'input text'")

