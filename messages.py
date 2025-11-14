from json_database import JSONDatabase

class Messages:
    def __init__(self, messages: list[dict] = [], max_chars_per_line: int = 26):
        self._max_messages = 25
        self._max_lines_per_message = 3
        self._messages = JSONDatabase("messages.json")
        for m in messages:
            self._messages.create(m)

        self._max_chars_per_line = max_chars_per_line
        self._max_chars_per_message = self._max_chars_per_line * self._max_lines_per_message

    def push_message(self, message: dict):
        if len(self.get_messages()) >= self._max_messages:
            self._messages.pop(-1)

        message["message"] = self.crop_message(message["message"])
        self._messages.create(message)

    def get_messages_string(self):
        out = ""
        for m in self._messages.read_all():
            out += f"from: {m["from"]}\n{self.crop_message(m["message"])}"
        return out

    def get_messages(self):
        return self._messages.read_all()

    def crop_message(self, message: str) -> str:
        cropped_message = message[:self._max_chars_per_message]
        separator = "\n"
        res = ""
        for i in range(0, len(cropped_message), self._max_chars_per_line):
            res += cropped_message[i:i + self._max_chars_per_line] + separator

        res += "\n"
        return res


def get_message_line_count(message: str):
    return len(message.split("\n"))


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

    message_board.push_message({"from": "Luke", "message": f"N{"O"*53}!"})

    print("-"*20)
    print(message_board.get_messages_string())