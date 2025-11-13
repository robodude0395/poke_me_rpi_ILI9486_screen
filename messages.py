class Messages:
    def __init__(self, messages: list[dict]):
        self._max_messages = 3
        self._messages = messages[0:self._max_messages]

    def push_message(self, message: dict):
        if len(self._messages) >= self._max_messages:
            self._messages.pop(-1)

        self._messages.insert(0, message)

    def get_messages_string(self):
        out = ""
        for m in self._messages:
            out += f"from: {m["from"]}:\n{m["message"]}\n\n"
        return out

if __name__ == "__main__":
    initial_messages = [
                {"from": "Santa", "message": "HO HO HO"},
                {"from": "Gandalf", "message": "You shall not pass!"},
                {"from": "Yoda", "message": "Do or do not. There is no try."},
                {"from": "Sherlock Holmes", "message": "Elementary, my dear Watson."}
                ]

    message_board = Messages(initial_messages)
    print("-"*20)

    print(message_board.get_messages_string())

    message_board.push_message({"from": "Darth Vader", "message": "I am your father."})

    print("-"*20)
    print(message_board.get_messages_string())

    message_board.push_message({"from": "Luke", "message": "NOOOOOOO!"})

    print("-"*20)
    print(message_board.get_messages_string())