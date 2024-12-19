import visualize
from conversation import Message, Name, Conversation

import json
from datetime import datetime
from matplotlib.backends.backend_pdf import PdfPages


def message_count(conversation : Conversation, pdf : PdfPages = None) -> None:
    visualize.message_count(conversation.messages_counter, conversation.participants, pdf=pdf)

def timeline(conversation : Conversation, pdf : PdfPages = None) -> None:
    hour_counts, weekday_counts, day_counts = conversation.timeline()
    visualize.hours(hour_counts, pdf=pdf)
    visualize.weekdays(weekday_counts, pdf=pdf)
    start, _ = conversation.time_interval()
    num_days = conversation.num_days()
    visualize.days(day_counts, start, num_days, pdf=pdf)

def emojis(conversation : Conversation, pdf : PdfPages = None) -> None:
    visualize.emojis(conversation.reaction_counter, conversation.emoji_counter, pdf=pdf)

def general_stats(conversation : Conversation, pdf : PdfPages) -> None:
    visualize.totals_and_averages(conversation, pdf)

def create_wrapped(conversation : Conversation) -> None:
    title = "".join([p.first_name for p in conversation.participants])
    with PdfPages(f"{title}.pdf") as pdf:
        visualize.frontpage(conversation, pdf)
        general_stats(conversation, pdf)
        message_count(conversation, pdf=pdf)
        timeline(conversation, pdf=pdf)
        emojis(conversation, pdf=pdf)

        # PDF info
        d = pdf.infodict()
        d['Title'] = f"{title}"
        d['Subject'] = f'Conversation statistics between {[p.first_name for p in conversation.participants]}'
        d['CreationDate'] = datetime.today()
        d['ModDate'] = datetime.today()

def preprocess(raw_names : list[str], raw_messages : list[dict], start_time : datetime = None) -> tuple[list[Name], Conversation]:
    conversation = Conversation(raw_names, raw_messages)
    if start_time is not None:
        def date_filter(date : datetime):
            def comp(m : Message):
                return m.time_stamp > date
            return comp
        conversation.messages = list(filter(date_filter(start_time), conversation.messages))

    return conversation

def main():
    start_time = datetime(year=2024, month=9, day=14)
    with open("data.json", encoding="utf8") as file:
        json_data = json.load(file)
        conversation = preprocess(json_data["participants"], json_data["messages"], start_time=start_time)
        create_wrapped(conversation)

if __name__ == '__main__':
    main()
