from conversation import Name, Conversation

from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime, timedelta
from collections import defaultdict
import emoji

def frontpage(conversation : Conversation, pdf : PdfPages):
    start, end = conversation.time_interval()
    first_page = plt.figure()
    first_page.clear()
    txt = f'''Messenger Wrapped™️ mellan\n
            {" och ".join([p.first_name for p in conversation.participants])}
            \n(data tagen mellan {start.date()} och {end.date()})'''
    first_page.text(0.5,0.5, txt, transform=first_page.transFigure, size=18, ha="center")
    pdf.savefig()
    plt.close()

def totals_and_averages(conversation : Conversation, pdf : PdfPages):
    plt.rcParams["font.family"] = "Segoe UI Emoji"
    generals_page = plt.figure()
    generals_page.clear()
    totals_text = f'''Sammanfattningar:\n
    ⭐{conversation.num_days()} dagar\n
    ⭐{conversation.tot_messages()} meddelanden\n
    ⭐{conversation.tot_words()} ord.
                    '''

    averages_text = f'''Snitt:\n
    💥{conversation.average_message_length()} ord per meddelande\n
    💥{conversation.average_messages_day()} meddelanden per dag.
                    '''

    generals_page.text(0.1, 0.5, totals_text, transform=generals_page.transFigure, size=14)
    generals_page.text(0.3, 0.2, averages_text, transform=generals_page.transFigure, size=14)
    pdf.savefig()
    plt.close()

def message_count(msg_count : dict[Name, int], participants : list[Name], pdf : PdfPages = None):
    def make_autopct(values):
        def my_autopct(pct):
            total = sum(values)
            val = int(round(pct*total/100.0))
            return '{v:d}\n({p:.1f}%)'.format(p=pct,v=val)
        return my_autopct

    fig, ax = plt.subplots()
    sizes = [msg_count[participant] for participant in participants]
    ax.pie(sizes, startangle=90, autopct=make_autopct(sizes))
    plt.legend([p.first_name for p in participants], loc="upper left")
    plt.axis("equal")
    plt.title("Antal skickade meddelanden")
    if pdf is not None:
        pdf.savefig()
        plt.close()
    else:
        plt.show()

def hours(hour_counts : dict[Name, list[int]], pdf : PdfPages = None):
    hours = list(range(24))
    fig, ax = plt.subplots()
    ax.yaxis.grid(linestyle='--')
    bottom = [0]*24
    for participant, messages in hour_counts.items():
        ax.bar(hours, messages, bottom=bottom, label=participant.first_name)
        bottom = [sum(x) for x in zip(bottom, messages)]

    ax.set_title("Meddelanden skickade per timma på dagen")
    ax.legend(loc="upper left")

    if pdf is not None:
        pdf.savefig()
        plt.close()
    else:
        plt.show()

def weekdays(weekday_counts : dict[Name, list[int]], pdf : PdfPages = None):
    weekdays = ["Må", "Ti", "On", "To", "Fr", "Lö", "Sö"]
    fig, ax = plt.subplots()
    ax.yaxis.grid(linestyle='--')
    bottom = [0]*7
    for participant, messages in weekday_counts.items():
        ax.bar(weekdays, messages, bottom=bottom, label=participant.first_name)
        bottom = [sum(x) for x in zip(bottom, messages)]

    ax.set_title("Meddelanden skickade per veckodag")
    ax.legend(loc="upper left")

    if pdf is not None:
        pdf.savefig()
        plt.close()
    else:
        plt.show()

def days(day_counts : dict[Name, list[int]], start : datetime, num_days : int, pdf : PdfPages = None):
    days = [start + timedelta(days=i) for i in range(num_days)]
    fig, ax = plt.subplots()
    ax.yaxis.grid(linestyle='--')
    bottom = [0]*num_days
    for participant, messages in day_counts.items():
        ax.bar(days, messages, bottom=bottom, label=participant.first_name)
        bottom = [sum(x) for x in zip(bottom, messages)]

    fig.autofmt_xdate()
    ax.set_title("Meddelanden skickade per dag")
    ax.legend(loc="upper left")
    if pdf is not None:
        pdf.savefig()
        plt.close()
    else:
        plt.show()

def emojis(reaction_counter : dict[Name, dict[str, int]], emoji_counter : dict[Name, dict[str, int]], num_emojis : int = 10, pdf : PdfPages = None):
    def deep_dsum(*dicts : dict[Name, dict[str, int]]) -> dict[Name, dict[str, int]]:
        ret = defaultdict(lambda: defaultdict(int))
        for d in dicts:
            for name in d.keys():
                for k, v in d[name].items():
                    ret[name][k] += v
        return ret

    def shallow_dsum(d : dict[Name, dict[str, int]]) -> dict[str, int]:
        ret = defaultdict(int)
        for name in d.keys():
            for k, v in d[name].items():
                ret[k] += v
        return ret

    plt.rcParams["font.family"] = "Segoe UI Emoji"

    fig, axs = plt.subplots(2, 2)
    ((ax1, ax2), (ax3, ax4)) = axs

    total_emoji_counter = deep_dsum(reaction_counter, emoji_counter)

    frequency_axs = [ax1, ax2, ax3]
    counters = [reaction_counter, emoji_counter, total_emoji_counter]
    titles = ["Vanligaste reaktionerna", "Vanligaste emojisar i text", "Vanligaste emojisar överlag"]

    for ax, counter, title in zip(frequency_axs, counters, titles):
        sorted_all = dict(sorted(shallow_dsum(counter).items(), key=lambda item: -item[1]))
        emojis = list(sorted_all.keys())[:num_emojis]
        reduced = {name: {k: counter[name][k] for k in emojis} for name in counter.keys()}
        ax.yaxis.grid(linestyle='--')
        bottom = [0]*num_emojis
        for participant, emoji_usages in reduced.items():
            ax.bar([emoji.emojize(e) for e in emojis], emoji_usages.values(), bottom=bottom, label=participant.first_name)
            bottom = [sum(x) for x in zip(bottom, emoji_usages.values())]
        ax.set_title(title)
        ax.legend(loc="upper right")

    participants = total_emoji_counter.keys()
    ax4.yaxis.grid(linestyle='--')
    bottom = [0]*len(participants)
    tags = ["Reaktioner", "Emojisar i text"]
    colors = ["tab:red", "tab:green"]
    for emoji_style, counter, color in zip(tags, counters[:-1], colors):
        xs = [p.first_name for p in participants]
        values = [sum([v for v in counter[p].values()]) for p in participants]
        ax4.bar(xs, values, bottom=bottom, label=emoji_style, color=color)
        bottom = [sum(x) for x in zip(bottom, values)]
    ax4.set_title("Emoji-användning mellan medverkande")
    ax4.legend(loc="upper left")

    plt.tight_layout()
    if pdf is not None:
        pdf.savefig()
        plt.close()
    else:
        plt.show()
