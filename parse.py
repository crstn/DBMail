import slate
import re

def parseBooking(pdffile):
    with open(pdffile) as f:
        text = slate.PDF(f)
        text = text[0] # we only need the first page

        print text

        # extract travel date
        parts = re.split('ltigkeit: ab ', text)
        parts = re.split('\n', parts[1])
        date = parts[0]

        parts = re.split('VON\n', text)
        parts = re.split('\n', parts[1])
        start = parts[0].decode("UTF-8")

        parts = re.split('->NACH\n->', text)
        parts = re.split('\n', parts[1])
        dest = parts[0].decode("UTF-8")

        parts = re.split('\nPreis\n\n', text)
        parts = re.split('\n', parts[1])
        price = parts[0]
        price = price[:-3].replace(',','.')

    return date, start, dest, price
