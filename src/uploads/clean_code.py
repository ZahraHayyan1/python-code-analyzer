def add(a, b):
    return a + b

def greet(name):
    return f"Hello, {name}!"

class User:
    def __init__(self, username):
        self.username = username

    def say_hello(self):
        return f"Welcome, {self.username}!"

if __name__ == "__main__":
    u = User("Iman")
    print(u.say_hello())
