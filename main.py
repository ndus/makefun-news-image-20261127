"""The World Today: an original, deterministic, standard-library newspaper renderer."""
import os
import struct
import zlib
from pathlib import Path

WIDTH = HEIGHT = 1000
SS = 2
PAPER = (246, 241, 227)
INK = (23, 20, 16)
CRIMSON = (163, 22, 33)

# Original single-line vector alphabet. Coordinates use a five-by-seven grid.
# A glyph is a tuple of independent pen strokes, each a polyline.
FONT = {
    'A': (((0,7),(0,2),(2.5,0),(5,2),(5,7)),((0,4),(5,4))),
    'B': (((0,7),(0,0),(3.5,0),(5,1),(5,2.5),(3.5,3.5),(0,3.5)),((3.5,3.5),(5,4.5),(5,6),(3.5,7),(0,7))),
    'C': (((5,1),(4,0),(1,0),(0,1),(0,6),(1,7),(4,7),(5,6)),),
    'D': (((0,0),(3,0),(5,2),(5,5),(3,7),(0,7),(0,0)),),
    'E': (((5,0),(0,0),(0,7),(5,7)),((0,3.5),(4,3.5))),
    'F': (((5,0),(0,0),(0,7)),((0,3.5),(4,3.5))),
    'G': (((5,1),(4,0),(1,0),(0,1),(0,6),(1,7),(5,7),(5,4),(3,4)),),
    'H': (((0,0),(0,7)),((5,0),(5,7)),((0,3.5),(5,3.5))),
    'I': (((0,0),(3,0)),((1.5,0),(1.5,7)),((0,7),(3,7))),
    'J': (((1,0),(5,0),(5,5.5),(3.5,7),(1,7),(0,6)),),
    'K': (((0,0),(0,7)),((5,0),(0,4),(5,7))),
    'L': (((0,0),(0,7),(5,7)),),
    'M': (((0,7),(0,0),(2.5,4),(5,0),(5,7)),),
    'N': (((0,7),(0,0),(5,7),(5,0)),),
    'O': (((1,0),(4,0),(5,1),(5,6),(4,7),(1,7),(0,6),(0,1),(1,0)),),
    'P': (((0,7),(0,0),(4,0),(5,1),(5,2.5),(4,3.5),(0,3.5)),),
    'Q': (((1,0),(4,0),(5,1),(5,5.5),(3.5,7),(1,7),(0,6),(0,1),(1,0)),((3,5),(5,7))),
    'R': (((0,7),(0,0),(4,0),(5,1),(5,2.5),(4,3.5),(0,3.5)),((2.5,3.5),(5,7))),
    'S': (((5,1),(4,0),(1,0),(0,1),(0,2.5),(1,3.5),(4,3.5),(5,4.5),(5,6),(4,7),(1,7),(0,6)),),
    'T': (((0,0),(5,0)),((2.5,0),(2.5,7))),
    'U': (((0,0),(0,6),(1,7),(4,7),(5,6),(5,0)),),
    'V': (((0,0),(2.5,7),(5,0)),),
    'W': (((0,0),(1,7),(2.5,3),(4,7),(5,0)),),
    'X': (((0,0),(5,7)),((5,0),(0,7))),
    'Y': (((0,0),(2.5,3.5),(5,0)),((2.5,3.5),(2.5,7))),
    'Z': (((0,0),(5,0),(0,7),(5,7)),),
    '0': (((1,0),(4,0),(5,1),(5,6),(4,7),(1,7),(0,6),(0,1),(1,0)),((1,6),(4,1))),
    '1': (((0,1.5),(2,0),(2,7)),((0,7),(4,7))),
    '2': (((0,1),(1,0),(4,0),(5,1),(5,2.5),(0,7),(5,7)),),
    '3': (((0,0),(4,0),(5,1),(5,2.5),(3,3.5),(5,4.5),(5,6),(4,7),(0,7)),((2,3.5),(3,3.5))),
    '4': (((4,7),(4,0),(0,5),(5,5)),),
    '5': (((5,0),(0,0),(0,3.5),(4,3.5),(5,4.5),(5,6),(4,7),(0,7)),),
    '6': (((5,0),(2,0),(0,2),(0,6),(1,7),(4,7),(5,6),(5,4.5),(4,3.5),(0,3.5)),),
    '7': (((0,0),(5,0),(1,7)),),
    '8': (((1,0),(4,0),(5,1),(5,2.5),(4,3.5),(1,3.5),(0,2.5),(0,1),(1,0)),((1,3.5),(0,4.5),(0,6),(1,7),(4,7),(5,6),(5,4.5),(4,3.5))),
    '9': (((5,3.5),(1,3.5),(0,2.5),(0,1),(1,0),(4,0),(5,1),(5,5),(3,7),(0,7)),),
    '.': (((0,6.5),(0,7)),),
    ',': (((1,6),(1,7),(0,8)),),
    "'": (((1,0),(0.5,2)),),
    '-': (((0,3.5),(3,3.5)),),
    ':': (((0,2),(0,2.5)),((0,5.5),(0,6))),
    ';': (((1,2),(1,2.5)),((1,5.5),(1,7),(0,8))),
    '!': (((0,0),(0,4.5)),((0,6.5),(0,7))),
    '?': (((0,1),(1,0),(4,0),(5,1),(5,2),(2.5,4),(2.5,5)),((2.5,6.5),(2.5,7))),
    '$': (((5,1),(1,1),(0,2),(1,3.5),(4,3.5),(5,5),(4,6),(0,6)),((2.5,0),(2.5,7))),
    '%': (((0,7),(5,0)),((0,0),(1.5,0),(1.5,2),(0,2),(0,0)),((3.5,5),(5,5),(5,7),(3.5,7),(3.5,5))),
    '+': (((0,3.5),(5,3.5)),((2.5,1),(2.5,6))),
    '/': (((0,7),(5,0)),),
    '(': (((2,0),(0,2),(0,5),(2,7)),),
    ')': (((0,0),(2,2),(2,5),(0,7)),),
    ' ': (),
}
GLYPH_WIDTH = {c: max((p[0] for s in strokes for p in s), default=2.5)
               for c, strokes in FONT.items()}
GLYPH_WIDTH[' '] = 2.6
CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,'-:;!?$%+/() "
assert set(FONT) == set(CHARSET.upper())


class Canvas:
    def __init__(self):
        self.w = WIDTH * SS
        self.h = HEIGHT * SS
        self.pixels = bytearray(bytes(PAPER) * (self.w * self.h))

    def rect(self, x, y, w, h, color=INK):
        x0, y0 = round(x * SS), round(y * SS)
        x1, y1 = round((x + w) * SS), round((y + h) * SS)
        assert 0 <= x0 <= x1 <= self.w and 0 <= y0 <= y1 <= self.h
        stripe = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            start = (yy * self.w + x0) * 3
            self.pixels[start:start + len(stripe)] = stripe

    def polygon(self, points, color=INK):
        vertices = [(x * SS, y * SS) for x, y in points]
        for yy in range(max(0, int(min(y for x,y in vertices))),
                        min(self.h, int(max(y for x,y in vertices)) + 1)):
            scan = yy + 0.5
            hits = []
            for (ax, ay), (bx, by) in zip(vertices, vertices[1:] + vertices[:1]):
                if min(ay,by) <= scan < max(ay,by):
                    hits.append(ax + (scan-ay) * (bx-ax) / (by-ay))
            hits.sort()
            for left, right in zip(hits[::2], hits[1::2]):
                a = max(0, int(left + 0.5))
                b = min(self.w, int(right + 0.5))
                start = (yy*self.w+a)*3
                self.pixels[start:start+(b-a)*3] = bytes(color)*(b-a)

    def line(self, x0, y0, x1, y1, thickness=1, color=INK):
        # Bresenham centerline with square nib; rendered at double resolution.
        x0,y0,x1,y1 = (round(v*SS) for v in (x0,y0,x1,y1))
        nib = max(1, round(thickness*SS))
        dx, sx = abs(x1-x0), 1 if x0 < x1 else -1
        dy, sy = -abs(y1-y0), 1 if y0 < y1 else -1
        error = dx+dy
        while True:
            a, b = x0-nib//2, y0-nib//2
            assert 0 <= a and a+nib <= self.w and 0 <= b and b+nib <= self.h
            stripe = bytes(color)*nib
            for yy in range(b,b+nib):
                start = (yy*self.w+a)*3
                self.pixels[start:start+nib*3] = stripe
            if x0 == x1 and y0 == y1:
                break
            twice = 2*error
            if twice >= dy:
                error += dy
                x0 += sx
            if twice <= dx:
                error += dx
                y0 += sy

    def png(self, path):
        # Box-filter supersampled pixels. No metadata or nondeterministic chunks.
        raw = bytearray()
        src = self.pixels
        stride = self.w*3
        for y in range(HEIGHT):
            raw.append(0)
            for x in range(WIDTH):
                i = ((y*SS)*self.w+x*SS)*3
                for c in range(3):
                    raw.append((src[i+c]+src[i+3+c]+src[i+stride+c]+src[i+stride+3+c]+2)//4)
        def chunk(kind, data):
            return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
        data = b'\x89PNG\r\n\x1a\n'
        data += chunk(b'IHDR',struct.pack('>IIBBBBB',WIDTH,HEIGHT,8,2,0,0,0))
        data += chunk(b'IDAT',zlib.compress(raw,9))
        data += chunk(b'IEND',b'')
        assert len(data) <= 1048576
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
        return len(data)


def measure(text, scale=1, aspect=1, gap=1.5):
    assert all(c in CHARSET for c in text), repr(text)
    return max(0, sum((GLYPH_WIDTH[c]+gap)*scale*aspect for c in text.upper())-gap*scale*aspect)


def text(canvas, message, x, y, scale=1, aspect=1, weight=0.65,
         color=INK, align='left', italic=False, gap=1.5, serif=False):
    width = measure(message,scale,aspect,gap)
    if align == 'center':
        x -= width/2
    elif align == 'right':
        x -= width
    for char in message.upper():
        for stroke in FONT[char]:
            points = [(x+(px+(7-py)*0.17*italic)*scale*aspect, y+py*scale)
                      for px,py in stroke]
            for a,b in zip(points,points[1:]):
                canvas.line(*a,*b,thickness=weight,color=color)
            if serif and len(stroke) > 1:
                for endpoint, neighbor in ((stroke[0],stroke[1]),(stroke[-1],stroke[-2])):
                    px,py = endpoint
                    if py in (0,7) and abs(py-neighbor[1]) > 1:
                        xx,yy = x+px*scale*aspect,y+py*scale
                        canvas.line(xx-0.43*scale*aspect,yy,xx+0.43*scale*aspect,yy,
                                    thickness=max(0.8,weight*0.66),color=color)
        x += (GLYPH_WIDTH[char]+gap)*scale*aspect
    return width


def wrap(message, width, scale=1, aspect=1, gap=1.5):
    result, line = [], ''
    for word in message.split():
        assert measure(word,scale,aspect,gap) <= width, word
        candidate = (line+' '+word).strip()
        if measure(candidate,scale,aspect,gap) > width:
            result.append(line)
            line = word
        else:
            line = candidate
    if line:
        result.append(line)
    return result


def paragraph(canvas, message, x, y, width, scale=1, aspect=1,
              leading=11, weight=0.65, color=INK, max_bottom=1000,
              italic=False, gap=1.5):
    lines = wrap(message,width,scale,aspect,gap)
    assert y+(len(lines)-1)*leading+8*scale+weight/2 <= max_bottom, (message,len(lines),y,max_bottom)
    for i,line in enumerate(lines):
        text(canvas,line,x,y+i*leading,scale,aspect,weight,color,italic=italic,gap=gap)
    return y+len(lines)*leading


def rule(canvas,y,thickness=0.7,x=28,width=944,color=INK):
    canvas.rect(x,y,width,thickness,color)


def masthead(canvas):
    text(canvas,'LATE EDITION',28,17,0.95,weight=0.7)
    text(canvas,'FRIDAY, NOVEMBER 27, 2026',500,17,0.95,weight=0.7,align='center')
    text(canvas,'ONE IMAGE - THE WHOLE DAY',972,17,0.95,weight=0.7,align='right')
    rule(canvas,32)
    title = 'THE WORLD TODAY'
    scale = 8.1
    aspect = 928 / measure(title,scale)
    text(canvas,title,500,46,scale,aspect,weight=3.8,align='center',gap=1.5,serif=True)
    rule(canvas,111,3)
    rule(canvas,117,0.7)
    text(canvas,"FRIDAY 27 NOVEMBER 2026 - THE DAY'S WORLD NEWS IN ONE IMAGE",500,126,1.08,weight=0.8,align='center')
    rule(canvas,142,0.7)


LEAD_BODY = "A projectile struck Saudi Aramco's 400,000-barrel-a-day Jazan refinery on Thursday, killing a Nepali worker, wounding several others and halting some operations, the Saudi energy ministry said. Iran's Revolutionary Guards said two tankers hit sea mines in the Strait of Hormuz. Brent crude climbed to $97.71 a barrel, on track for its first weekly gain in four weeks, with $100 in reach."
UKRAINE_BODY = "Russia launched 155 attack drones overnight, 83 of them jet-powered Shaheds. Air defences downed 110, but strikes hit 27 locations; one man was killed in Zaporizhzhia and 16 people were hurt. Estonia issued an air-threat warning and NATO jets scrambled."
STORIES = [
    ('EUROPE', 'EU DEADLOCKED ON BUDGET AND UKRAINE LOAN',
     'Leaders ended 12 hours of Brussels talks with no deal on the 2028-34 budget. 24 states back a 45-billion-euro loan for Ukraine in 2027; the decision slips to December. Leaders did choose De Cos as the next ECB president.'),
    ('GAZA', 'STRIKES KILL 10, SENIOR HAMAS FIGURE AMONG DEAD',
     'Israeli strikes killed 10 Palestinians across Gaza on Thursday, hospital officials said, including senior Hamas official Khaled Abu Nada, hit in Deir al-Balah - the third senior figure killed since Tuesday.'),
    ('KUWAIT', 'DRONES REACH KUWAIT',
     'Iranian drones struck a vital facility in Kuwait. Two Italians were killed, and four people were hurt by falling debris from interceptions, the Kuwaiti army said.'),
    ('AFRICA', 'EBOLA PASSES 12,000 CASES IN CONGO',
     'The outbreak reached 12,021 confirmed infections and 5,904 deaths, the health ministry said, as fighting in Ituri forces response teams to pull back.'),
    ('ASIA-PACIFIC', 'TAIWAN VOTES ON ITS NUCLEAR FUTURE',
     'Taiwan holds nine-in-one local elections on Saturday beside a referendum on ending the nuclear-free homeland policy. 20.0 million people can vote in the referendum; a yes needs 5,000,959 votes. China flew 30 military sorties on Friday.'),
    ('PACIFIC', 'NEW ZEALAND PARLIAMENT DEADLOCKED',
     'The final election count left parliament split down the middle: the ruling coalition holds 65 of 130 seats, short of a working majority.'),
    ('DIPLOMACY', 'NORTH KOREA PAUSES AID TO RUSSIA',
     "Kyiv's military intelligence says Pyongyang has halted military aid to Moscow, including KN-23 ballistic missiles and artillery shells."),
    ('TRADE', 'PARTNERS REJECT NEW US TARIFF CASE',
     "US trading partners pushed back against Washington's new tariff justification, while President Trump said he had urged Putin to pull back aggression across Europe."),
    ('DEFENCE', 'ERDOGAN SEALS MECCA DEFENCE PACT',
     "President Erdogan formally approved the Mecca joint defence agreement with Saudi Arabia and Pakistan, completing Turkey's ratification of the pact."),
]
EGYPT_BODY = "At least 31 people died when a fuel tanker collided and caught fire near the Egyptian capital, one of the day's deadliest accidents."
SPORT_BODY = 'Europa League: AC Milan came from 2-0 down to win 4-2 at Olympiacos, Viktoria Plzen stunned Benfica 4-0, and Bournemouth stayed perfect with a 2-1 win at Celta Vigo. NFL Thanksgiving: Bears 39-35 Lions on a touchdown with 3 seconds left; Eagles 39-38 Cowboys after trailing by 21; Bills 13-10 Chiefs on a 57-yard field goal as time expired.'
NUMBERS = [
    ('155', 'DRONES LAUNCHED AT UKRAINE'),
    ('110', 'DRONES SHOT DOWN'),
    ('$97.71', 'BRENT CRUDE, PER BARREL'),
    ('12,021', 'EBOLA CASES IN CONGO'),
    ('5,000,959', 'YES VOTES TAIWAN NEEDS'),
    ('31', 'DEAD IN CAIRO TANKER FIRE'),
]



def refinery_pictogram(canvas, x, y):
    """Original 134-by-78 refinery silhouette, drawn only with lines and rectangles.

    Tanks, pipework, fractionating columns and a crimson flare occupy the
    ragged-right space beside the two shorter lead-headline lines.
    """
    def line(ax, ay, bx, by, thickness=1.3, color=INK):
        canvas.line(x+ax,y+ay,x+bx,y+by,thickness,color)
    def rect(ax, ay, w, h, color=INK):
        canvas.rect(x+ax,y+ay,w,h,color)

    # Common ground line and low storage tanks with stepped domed roofs.
    rect(0,76,134,2)
    rect(2,58,35,18)
    rect(5,54,29,4)
    rect(10,51,19,3)
    rect(43,63,26,13)
    rect(46,59,20,4)
    line(6,63,32,63,1,PAPER)
    line(6,67,32,67,1,PAPER)
    # Tall distillation column, service platforms and a slim flare stack.
    rect(75,30,10,46)
    rect(77,26,6,4)
    rect(96,43,8,33)
    rect(117,24,5,52)
    for level in (37,49,61):
        rect(71,level,18,2)
        line(71,level-3,89,level-3,0.8)
        line(71,level-3,71,level,0.8)
        line(89,level-3,89,level,0.8)
    line(92,35,92,75,1)
    for level in range(38,74,6):
        line(89,level,95,level,0.8)
    # Right-angle overhead pipes join the refinery vessels.
    line(35,69,43,69,2)
    line(55,59,55,46,2)
    line(55,46,75,46,2)
    line(85,68,99,68,2)
    line(99,68,99,58,2)
    line(104,58,119,58,2)
    # An irregular flame: crimson outline and a paper-colored inner lick.
    line(119,23,113,17,3,CRIMSON)
    line(113,17,114,11,3,CRIMSON)
    line(114,11,120,3,3,CRIMSON)
    line(120,3,120,12,3,CRIMSON)
    line(120,12,124,8,3,CRIMSON)
    line(124,8,127,17,3,CRIMSON)
    line(127,17,122,23,3,CRIMSON)
    line(122,23,119,23,3,CRIMSON)
    line(119,21,120,16,1.3,CRIMSON)


def drone_pictogram(canvas, x, y):
    """Original top-view delta-wing drone; its 126-by-64 box is text-free."""
    def line(ax, ay, bx, by, thickness=1.5, color=INK):
        canvas.line(x+ax,y+ay,x+bx,y+by,thickness,color)
    # Symmetric swept wings, built as thick, tapering line bundles.
    for offset in range(8):
        line(63,6+offset,7+offset,49,1.6)
        line(63,6+offset,119-offset,49,1.6)
    line(7,49,55,40,3)
    line(119,49,71,40,3)
    line(55,40,60,53,3)
    line(71,40,66,53,3)
    canvas.rect(x+60,y+14,6,41)
    line(60,14,63,3,2)
    line(63,3,66,14,2)
    # Rear propeller and a restrained crimson hub.
    line(63,53,63,60,2)
    line(48,59,78,59,1.8)
    canvas.rect(x+61,y+57,4,4,CRIMSON)
    line(63,19,63,37,1,PAPER)


def rest_of_page(canvas):
    text(canvas,'MIDDLE EAST - ENERGY',28,157,1.12,weight=0.9,color=CRIMSON)
    for i,line in enumerate(('REFINERY STRUCK,','OIL SURGES','TOWARD $100')):
        text(canvas,line,28,180+i*42,5.0,1.075,weight=3.0,gap=1.15,serif=True)
    refinery_pictogram(canvas,408,222)
    paragraph(canvas,"Houthi projectile hits Aramco's Jazan plant - tankers strike mines in Hormuz",
              28,311,516,1.34,0.89,15,0.8,italic=True,max_bottom=344)
    paragraph(canvas,LEAD_BODY,28,352,516,1.05,0.85,11.4,0.85,max_bottom=416)
    canvas.rect(558,155,0.6,262)
    text(canvas,'UKRAINE WAR',577,157,1.12,weight=0.9,color=CRIMSON)
    for i,line in enumerate(('155 DRONES','OVER UKRAINE')):
        text(canvas,line,577,181+i*32,3.5,0.94,weight=2.0,gap=1.3,serif=True)
    drone_pictogram(canvas,839,175)
    paragraph(canvas,UKRAINE_BODY,577,254,395,1.19,0.94,13.7,0.85,max_bottom=344)
    # A compact boxed wire digest underneath the second story.
    canvas.rect(576,352,396,0.7)
    canvas.rect(576,416,396,0.7)
    canvas.rect(576,352,0.7,64)
    canvas.rect(971.3,352,0.7,64)
    text(canvas,'ALSO FRIDAY',586,361,1.02,weight=0.9,color=CRIMSON)
    for i,line in enumerate((
            'London: 24-hour Tube strike brings travel chaos',
            'Britain contacts 100,000 veterans over readiness',
            'Serbia sets presidential vote for 27 December')):
        assert measure(line,0.98,0.92) <= 376
        text(canvas,line,586,377+i*11.5,0.98,0.92,weight=0.8)
    rule(canvas,429,1.4)
    # Three columns, three complete rows, then the final full-width brief.
    for i,(section,headline,body) in enumerate(STORIES):
        row,col = divmod(i,3)
        x,y = 28+322*col,441+102*row
        text(canvas,section,x,y,1.02,weight=0.9,color=CRIMSON)
        paragraph(canvas,headline,x,y+16,300,1.69,0.86,15.5,1.3,max_bottom=y+49)
        # Share a body baseline within each row, using its tallest headline.
        # One-line rows stay compact; the first row reserves two headline lines.
        row_headlines = STORIES[row*3:row*3+3]
        headline_lines = max(len(wrap(item[1],300,1.69,0.86))
                             for item in row_headlines)
        body_y = y+16+headline_lines*15.5+7
        paragraph(canvas,body,x,body_y,300,1.0,0.86,10.4,0.8,max_bottom=y+94,gap=1.25)
        if row < 2:
            rule(canvas,y+94,0.5,x,300)
    canvas.rect(339,440,0.5,299)
    canvas.rect(661,440,0.5,299)
    rule(canvas,748,0.6)
    text(canvas,'EGYPT',28,759,1.02,weight=0.9,color=CRIMSON)
    text(canvas,'31 DIE IN TANKER FIRE NEAR CAIRO',102,756,1.88,0.9,weight=1.05)
    paragraph(canvas,EGYPT_BODY,28,779,944,1.06,0.99,12,0.8,max_bottom=800)
    rule(canvas,806,1.4)
    text(canvas,'SPORT',28,819,1.15,weight=1.0,color=CRIMSON)
    text(canvas,'COMEBACK NIGHT IN EUROPE - AND THREE NFL THRILLERS',104,816,2.03,0.94,weight=1.1)
    paragraph(canvas,SPORT_BODY,28,842,944,1.11,0.96,13,0.85,max_bottom=885)
    rule(canvas,889,1.5)
    text(canvas,'THE DAY IN NUMBERS',500,899,1.08,weight=0.9,color=CRIMSON,align='center')
    for i,(number,caption) in enumerate(NUMBERS):
        left = 28+i*944/6
        center = left+944/12
        if i:
            canvas.rect(left,919,0.5,44)
        # Reserve a consistent inset and a four-pixel gap below the figures.
        size = min(3.1,137/measure(number,1,0.9))
        text(canvas,number,center,918,size,0.9,weight=1.6,align='center')
        lines = wrap(caption,144,0.89,0.92)
        assert len(lines) <= 2
        for j,line in enumerate(lines):
            text(canvas,line,center,949+j*10,0.89,0.92,weight=0.8,align='center')
    rule(canvas,970,0.7)
    text(canvas,"COMPILED FROM THE DAY'S WIRE REPORTS - FRIDAY 27 NOVEMBER 2026",500,980,0.96,weight=0.65,align='center')
    rule(canvas,994,0.7)


def main():
    canvas = Canvas()
    masthead(canvas)
    rest_of_page(canvas)
    path = Path(os.environ.get('MAKEFUN_OUTPUT_DIR','/output'))/'entry.png'
    size = canvas.png(path)
    print(f'{path}: {WIDTH}x{HEIGHT} RGB PNG, {size} bytes')


if __name__ == '__main__':
    main()
