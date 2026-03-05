
import mido
import os
import sys
from PIL import Image, ImageFont, ImageDraw
# Middle C (note #60 is C3 or C4)

path = os.path.dirname(sys.argv[0])
fileName = 'D:/Musique/_Midi/Ode_to_Joy_Easy_variation_torbyBrand.mid'
scoreName = os.path.split(fileName)[1]
notesImgPath = os.path.join(path, 'NotesImages/')
if os.path.isfile(fileName) is False or os.path.isdir(notesImgPath) is False:
    raise NameError("Wrong File Path")

noteNameList = ['Do', "Reb", "Re", "Mib", "Mi", "Fa", "Solb", "Sol", "Lab", "La", "Sib", "Si"]

def setNoteName(msg, noteNameList):
    octave = int(msg.note / 12) - 2
    noteIdx = msg.note % 12
    noteName = noteNameList[noteIdx]
    # print(msg.note, octave, note)
    msg.__dict__['octave'] = octave
    msg.__dict__['noteIdx'] = noteIdx
    msg.__dict__['noteName'] = noteName
    return msg

def midiNoteRange(noteNameList):
    noteDict = {}
    msg = mido.Message.from_dict({'type': 'note_on'})
    for noteIdx in range(128):
        msg.__dict__['note'] = noteIdx
        msg = setNoteName(msg, noteNameList)
        noteDict[noteIdx] = '{}{}'.format(msg.noteName, msg.octave)
    return noteDict

def setMidiColoredIcons(notesImgPath, fullMidiNoteNameDict):
    scoreIcons = {}
    for noteIdx in fullMidiNoteNameDict.keys():
        fileName = fullMidiNoteNameDict[noteIdx]+'.jpg'
        path = os.path.join(notesImgPath, fileName)
        if os.path.isfile(path):
            img = None
        else:
            print('icon not found : {}'.format(path))
            img = None
        scoreIcons[noteIdx] = img
    return scoreIcons

def setNewScoreSheet(scoreName):
    scoreImg = Image.new('RGBA', (ux['x_res'], ux['y_res']), (255, 255, 255, 255))

    # set sheet title
    draw = ImageDraw.Draw(scoreImg)
    fontSize = 50
    font = ImageFont.truetype('arial.ttf', size=fontSize)
    draw.text((ux['margin']*2, ux['margin'] - fontSize * 2), scoreName, (0, 0, 0), font=font)

    idx = 0
    while True:
        linexy = [ux['margin']-25, ux['margin'] + idx*(ux['height']+ux['y_padding']), ux['x_res'] - ux['margin']]
        if linexy[1] > ux['y_res']-ux['margin']:
            break

        trebbleClefImg = Image.open(os.path.join(notesImgPath, 'trebbleClef.png'))
        emptyImg = Image.new('RGBA', scoreImg.size, (255, 255, 255, 0))
        emptyImg.paste(trebbleClefImg, (linexy[0]-50, linexy[1]-25))
        scoreImg = Image.alpha_composite(scoreImg, emptyImg)  # bad paste no alpha

        draw = ImageDraw.Draw(scoreImg)
        draw.line([(linexy[0], linexy[1]), (linexy[2], linexy[1])], fill='black', width=3)
        draw.line([(linexy[0], linexy[1] + ux['height'] * 0.25), (linexy[2], linexy[1] + ux['height'] * 0.25)], fill='black', width=3)
        draw.line([(linexy[0], linexy[1] + ux['height'] * 0.5), (linexy[2], linexy[1] + ux['height'] * 0.5)], fill='black', width=3)
        draw.line([(linexy[0], linexy[1] + ux['height'] * 0.75), (linexy[2], linexy[1] + ux['height'] * 0.75)], fill='black', width=3)
        draw.line([(linexy[0], linexy[1] + ux['height']), (linexy[2], linexy[1] + ux['height'])], fill='black', width=3)
        idx += 1
    return scoreImg

def saveScoreSheet(scoreImg, scoreIdx, path, scoreName):
    path = os.path.join(path, 'coloredScore.{}.{}.png'.format(scoreName, scoreIdx))
    scoreImg.save(path)
    print('Score saved to {}'.format(path))

fullMidiNoteNameDict = midiNoteRange(noteNameList)
print(fullMidiNoteNameDict)
midi = mido.MidiFile(fileName)

notes = []
for i, track in enumerate(midi.tracks):
    # print('Track {}: {}'.format(i, track.name))
    for msg in track:
        # print(msg, msg.__dict__)
        if msg.type == 'note_on' and msg.velocity != 0:
            notes.append(msg.note)

print()
print('----------')
print('Partition de Gaël')
print('----------')
print()

ux = {'width': 200,
      'height': 200,
      'x_padding': 50,
      'y_padding': 200,
      'margin': 300,
      'x_res' : 3508,
      'y_res': 2480,
      }
scoreImg = setNewScoreSheet(scoreName)
defaultImg = Image.new('RGBA', (ux['width'], ux['height']), (200, 200, 200, 255))
scoreColoredIconsDict = {'default': defaultImg}
x = ux['margin']+75
y = ux['margin']

scoreIdx = 0
for note in notes:
    # print(note.note, note.octave, note.noteIdx, note.noteName)
    print(note)
    if note in scoreColoredIconsDict.keys():
        img = scoreColoredIconsDict[note]
    else:
        fileName = fullMidiNoteNameDict[note] + '.png'
        imgPath = os.path.join(notesImgPath, fileName)
        if os.path.isfile(imgPath):
            img = Image.open(imgPath)
            scoreColoredIconsDict[note] = img
        else: # set as default
            img = scoreColoredIconsDict['default']
            print('note not found: '+fullMidiNoteNameDict[note])

    #img is set. comp it to full score
    emptyImg = Image.new('RGBA', scoreImg.size, (255, 255, 255, 0))
    emptyImg.paste(img, (x, y))
    scoreImg = Image.alpha_composite(scoreImg, emptyImg)  # bad paste no alpha
    newx = x + ux['width'] + ux['x_padding']
    if newx + ux['width'] < ux['x_res']-ux['margin']:
        x = newx
    else:
        x = ux['margin']+75
        newy = y + ux['height'] + ux['y_padding']
        if newy + ux['height'] < ux['y_res']-ux['margin']:
            y = newy
        else:
            # new image is needed
            saveScoreSheet(scoreImg, scoreIdx, path, scoreName)
            scoreIdx += 1
            scoreImg = setNewScoreSheet(scoreName)
            x = ux['margin']+75
            y = ux['margin']

saveScoreSheet(scoreImg, scoreIdx, path, scoreName)

#generate pdf
imageList = []
for i in range(scoreIdx+1):
    imgPath = os.path.join(path, 'coloredScore.{}.{}.png'.format(scoreName, i))
    if i == 0:
        img = Image.open(imgPath).convert('RGB')
    else:
        imageList.append(Image.open(imgPath).convert('RGB'))

img.save(os.path.join(path, 'coloredScore.{}.pdf'.format(scoreName)), save_all=True, append_images=imageList)
print('Done')