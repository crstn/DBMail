import slate
import re

def parseBooking(pdffile):
    with open(pdffile) as f:
        text = slate.PDF(f)
        text = text[0] # we only need the first page

        # two different ticket layouts:
        if 'ltigkeit: ab ' in text:

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

        else:
             parts = re.split('Fahrtantritt am ', text)
             parts = re.split('\n', parts[1])
             date = parts[0]

             parts = re.split('\nVIA:', text)
             start = re.split('\n', parts[0])
             start = start[len(start)-1].decode("UTF-8")

             dest = re.split('\n', parts[1])
             dest = dest[2].strip()
             if(', mit ' in dest):
                 dest = re.split(', mit ', dest)
                 dest = dest[0]
             dest = dest.decode("UTF-8")

        # price is in the same place in both layouts
        parts = re.split('\nPreis\n\n', text)
        parts = re.split('\n', parts[1])
        price = parts[0]
        price = price[:-3].replace(',','.')


    return date, start, dest, price
