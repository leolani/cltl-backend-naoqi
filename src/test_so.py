import qi

module_name = "TestModule"

app = qi.Application(["Test App", "--qi-url=192.168.1.176:9559", "--qi-listen-url=tcp://0.0.0.0:9558"])

class TestModule(object):
    def test(self):
        print("Running test on TestModuleB")
        return "called test of TestModuleB"


testModule = TestModule()

app.start()
session = app.session
session.listen("tcp://0.0.0.0:9558")

session = app.session.services()

app.session.registerService("TestModule", TestModule)

session = app.session.services()

