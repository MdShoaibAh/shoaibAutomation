def test_fun():
    print("test 1")
    assert 10==11

def test_fun1():
    print("test 2")
    assert 10!=11

def test_fun2():
    print("test 3")
    assert "10" == "10"

def test_fun3():
    print("test 3")
    assert "10" == "hello"

def test_fun4():
    print("test 3")
    assert "10" == "thanks"
