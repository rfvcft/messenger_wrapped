from collections import defaultdict
from datetime import datetime
import emoji

class Name:
    def __init__(self, name : str):
        self.full_name = name
        self.first_name, self.last_name = name.split()

    def __repr__(self):
        return f'Name({self.full_name})'

    def __eq__(self, other):
        if isinstance(other, Name):
            return self.full_name == other.full_name
        return False

    def __hash__(self):
        return hash(self.full_name)

    def __lt__(self, other):
        return self.full_name > other.full_name


class Reaction:
    def __init__(self, actor : str, reaction : str):
        self.actor = Name(actor)
        self.reaction = reaction

    def __repr__(self):
        return f'Reaction({self.actor}, {self.reaction})'


class Media:
    def __init__(self, uri : str = None):
        self.uri = uri


class Message:
    def __init__(self, sender_name : str, message_type : str, text : str, reactions : list[dict], time_stamp : int, media : list, is_unsent : bool):
        self.sender = Name(sender_name)
        self.type = message_type
        self.text = text
        self.reactions = self.to_reactions(reactions)
        self.time_stamp = self.to_date_time(time_stamp)
        self.media = self.to_media(media)

    def __repr__(self):
        return f'Message({self.sender},{self.type},{self.text},{self.reactions},{self.time_stamp},{self.media})'

    def to_reactions(self, reactions : list[dict]) -> list[Reaction]:
        return [Reaction(reaction["actor"], reaction["reaction"]) for reaction in reactions]

    def to_date_time(self, time_stamp : int) -> datetime:
        return datetime.fromtimestamp(time_stamp // 1000)

    def to_media(self, media : list[dict]) -> Media:
        if media:
            return Media(media[0]["uri"])
        else:
            return Media()


class Conversation:
    def __init__(self, raw_names : list[str], raw_messages : list[dict]):
        self.messages = self.to_messages(raw_messages)
        self.participants = self.to_names(raw_names)
        self.messages_counter = self.count_messages()
        self.word_counter = self.count_words()
        self.emoji_counter = self.count_emojis()
        self.reaction_counter = self.count_reactions()

    def to_names(self, raw_names : list[str]) -> list[Name]:
        return [Name(name) for name in raw_names]

    def to_messages(self, raw_messages : list[dict]) -> list[Message]:
        return [Message(sender_name=msg["senderName"],
                        message_type=msg["type"],
                        text=msg["text"],
                        reactions=msg["reactions"],
                        time_stamp=msg["timestamp"],
                        media=msg["media"],
                        is_unsent=msg["isUnsent"]) for msg in raw_messages]

    def count_messages(self) -> defaultdict[Name, int]:
        messages_counter = defaultdict(int)
        for message in self.messages:
            messages_counter[message.sender] += 1
        return messages_counter

    def count_words(self) -> defaultdict[Name, int]:
        word_counter = defaultdict(int)
        for message in self.messages:
            if message.type == "text":
                num_words = len(message.text.split())
                word_counter[message.sender] += num_words
        return word_counter

    def count_reactions(self) -> defaultdict[str, defaultdict[str, int]]:
        reaction_counter = defaultdict(lambda: defaultdict(int))
        for message in self.messages:
            for reaction in message.reactions:
                reaction_counter[reaction.actor][emoji.demojize(reaction.reaction)] += 1
        return {k: v for k, v in sorted(reaction_counter.items(), key=lambda item: item[0])}

    def count_emojis(self) -> defaultdict[str, defaultdict[str, int]]:
        emoji_counter = defaultdict(lambda: defaultdict(int))
        for message in self.messages:
            for e in emoji.analyze(message.text):
                emoji_counter[message.sender][emoji.demojize(e.chars)] += 1
        return {k: v for k, v in sorted(emoji_counter.items(), key=lambda item: item[0])}

    def tot_messages(self) -> int:
        return sum([ms for ms in self.messages_counter.values()])

    def tot_words(self) -> int:
        return sum([ws for ws in self.word_counter.values()])

    def time_interval(self) -> tuple[datetime, datetime]:
        start = self.messages[0].time_stamp
        end = self.messages[-1].time_stamp
        return start, end

    def num_days(self) -> int:
        start, end = self.time_interval()
        return (end - start).days + 1

    def average_message_length(self) -> float:
        return round(self.tot_words() / self.tot_messages(), 2)

    def average_messages_day(self) -> float:
        return round(self.tot_messages() / self.num_days(), 2)

    def timeline(self) -> tuple[dict[Name, list[int]], dict[Name, list[int]], dict[Name, list[int]]]:
        start, _ = self.time_interval()

        participant_hours =     {p: [0]*24              for p in self.participants}
        participant_weekdays =  {p: [0]*7               for p in self.participants}
        participant_days =      {p: [0]*self.num_days() for p in self.participants}

        for message in self.messages:
            date = message.time_stamp
            hour, weekday, day = date.hour, date.weekday(), (date-start).days
            participant_hours[message.sender][hour] += 1
            participant_weekdays[message.sender][weekday] += 1
            participant_days[message.sender][day] += 1

        return participant_hours, participant_weekdays, participant_days
