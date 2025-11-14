from json_database import JSONDatabase


class Messages:
    def __init__(self, messages=None, json_path="", max_chars_per_line: int = 26):
        if messages is None:
            messages = []

        self._max_messages = 25
        self._max_lines_per_message = 3
        self._max_chars_per_line = max_chars_per_line
        self._max_chars_per_message = self._max_chars_per_line * self._max_lines_per_message

        # Use an in-memory override so JSONDatabase behaves like a list
        if json_path == "":
            self._messages = JSONDatabase(dictionary_override=[])
        else:
            self._messages = JSONDatabase(json_path)

        for m in messages:
            self._messages.create(m)

    # -------------------------------------------------------------

    def push_message(self, message: dict):
        """Add a new message, cropping and enforcing capacity."""
        all_msgs = self.get_messages()

        # Remove oldest if over capacity
        if len(all_msgs) >= self._max_messages:
            all_msgs.pop(0)  # remove the FIRST message (oldest)

        # Crop text
        message["message"] = self.crop_message(message["message"])

        all_msgs.append(message.copy())
        self._messages._save(all_msgs)

    # -------------------------------------------------------------

    def get_messages(self):
        return self._messages.read_all()

    # -------------------------------------------------------------

    def get_messages_string(self):
        """Return all messages in readable format."""
        out_lines = []

        for m in self.get_messages():
            from_field = m.get("from", "Unknown")
            msg = m.get("message", "")
            msg = self.crop_message(msg)
            out_lines.append(f"from: {from_field}\n{msg}")

        return "\n".join(out_lines)

    # -------------------------------------------------------------

    def crop_message(self, message: str) -> str:
        """Crop a message to max characters & break into lines."""
        cropped = message[:self._max_chars_per_message]

        lines = [
            cropped[i : i + self._max_chars_per_line]
            for i in range(0, len(cropped), self._max_chars_per_line)
        ]

        return "\n".join(lines) + "\n"

    # -------------------------------------------------------------


def get_message_line_count(message: str):
    return len(message.split("\n"))


# -------------------------------------------------------------
# Standalone test
# -------------------------------------------------------------
if __name__ == "__main__":
    initial_messages = [
        {"from": "Santa", "message": "HO HO HO"},
        {"from": "Gandalf", "message": "You shall not pass!"},
        {"from": "Yoda", "message": "Do or do not. There is no try."},
        {"from": "Sherlock Holmes", "message": "Elementary, my dear Watson."}
    ]

    message_board = Messages(initial_messages)

    print("-" * 20)
    print(message_board.get_messages_string())

    message_board.push_message({"from": "Darth Vader", "message": "I am your father."})

    print("-" * 20)
    print(message_board.get_messages_string())

    long_no = "N" + ("O" * 53) + "!"
    message_board.push_message({"from": "Luke", "message": long_no})

    print("-" * 20)
    print(message_board.get_messages_string())
