import time

# from app import db
#
# print(db.insert("jirka", "ad", "123"))
# print(db.check_name("jirka"))
# print(db.check_name("ja"))
from types import NoneType

print(len("sha256$wIYLrmxZF6Vpo2qt$1ad56207e270e82a99ba5be1ec5217f3ffd1969b34f07a8d9bd880b9bdac11b9"))

print(type(("email")))
print(type(("neco",)))


def neco():
    return "asdasd", 1, "adasddddddd"


print(type(neco()))

print(*neco())


def bk(aloha):
    if not aloha is None:
        if aloha == 1:
            print("tisknu 1")
    else:
        print("ostatní")


bk(None)
bk(1)
bk(2)

if "aloha":
    print("adads")

asdas = ["adasd", 1, "gopre", "asdkjl", 5465]

print(*asdas)


def smt():
    return 5, 8, 6


def gsasdlk(x, y, z):
    print("Tisknu", x + y + z)


gsasdlk(*smt())

haha = []


def kilo():
    global haha
    if not haha:
        haha = ["adasd", 1, "gopre", "asdkjl", 5465]

    if haha:
        if isinstance(haha, list):
            user = haha.pop(0)
            return user
        else:
            return haha
    else:
        return "No possible matches"


def kkt():
    print(kilo())
    print(haha)


for i in range(6):
    kkt()


def jil(data):
    return [user for user in data]


print(jil([]))

for x in []:
    print("Jsem tu?", x)

gid = ["adasd", 1, "gopre", "asdkjl", 5465]

print(gid)


def sadad(neco):
    neco.pop(0)


def kolo():
    sadad(gid)


kolo()
print(gid)
neco = 1
nic = 0
bla = "adad"

print(bla == False)


def hmm(pet: int):
    print(pet)


hmm(4)
hmm("ahoj")

al = "[\"4\"]"
print(list(al))
print(list(al[1:-1]))

kaka = {"dssd": 1, "ooo": "dsa"}


adadsasd
response = False
print("asdasdsadsaddsa")

aloha = (12,12,3)
print(type(aloha))
aloha = None
if isinstance(aloha, (tuple, NoneType)):
    print("funguje")


huuu = "asdaddas"
print(huuu[:5])

data = ""
print([data for msg in data])

ku = None
if ku:
    print("kolo")