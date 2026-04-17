# WARNING: This code is intentionally bad 😈

import random, sys, os

DATA = ["1", 2, None, "hello", "", -5, 3.14, "999999999999999999999999"]

global_var = 0

def doStuff(x, y=None):
    global global_var
    try:
        if x == None:
            x = "0"
        if type(x) == str:
            if x.isdigit():
                x = int(x)
            else:
                x = float(len(x))
        if y:
            result = x / y
        else:
            result = x / random.choice([0, 1, 2])  # possible ZeroDivisionError

        if result > 10:
            print("Big number: " + str(result))
        elif result < 0:
            print("Negative??", result)
        else:
            print("meh", result)

        global_var += result

        if result == 13:
            raise Exception("Unlucky number!")

        return result

    except:
        pass  # swallowing all errors 😬

def recursiveMess(n):
    if n <= 0:
        return "done"
    else:
        return recursiveMess(n - 1) + str(n)

def weirdLoop():
    i = 0
    while True:
        i += 1
        if i % 7 == 0:
            continue
        if i > 50:
            break
        print("Loop:", i)

def fileChaos():
    try:
        f = open("non_existent_file.txt", "r")
        data = f.read()
        f.close()
        return data
    except:
        return None

def mutateList(lst):
    for i in range(len(lst)):
        if type(lst[i]) == int:
            lst[i] = lst[i] * random.choice([None, 2, "x"])
        elif lst[i] == "":
            lst.remove(lst[i])  # modifying list while iterating 💀
    return lst

def main():
    results = []
    for item in DATA:
        res = doStuff(item, random.choice([None, 0, 1, 5]))
        results.append(res)

    print("Recursive:", recursiveMess(5))
    weirdLoop()

    chaos = fileChaos()
    print("File data:", chaos)

    print("Mutated:", mutateList(DATA))

    # weird dictionary usage
    d = {}
    for i in range(10):
        d[i] = i * i
    for k in d:
        if k == 5:
            del d[k]  # modifying dict during iteration 😵

    print("Dict:", d)

    # pointless nested conditions
    x = random.choice([True, False])
    if x:
        if not x == False:
            if x is True:
                print("Confusing truth")

    # random system call
    os.system("echo Running something useless...")

if __name__ == "__main__":
    main()