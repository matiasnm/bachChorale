from music21 import *
import copy

##################################################################################
#chordify to close position chords, removes ties and runs roman numeral analysis
#key is manual input!?
def romanAnalysis(score):
    chords = score.chordify()
    key = score.analyze('key')
    chords.partName = "Chords"
    chords.partId = "Chords"
    chords.partAbbreviation = "Chords"
    chords._partAbbreviation = "Chords"
    
    for c in chords[chord.Chord]:
        offset = c._activeSiteStoredOffset
        if offset==int(offset):
            #print(offset) #offset by measure
            c.closedPosition(forceOctave=4, inPlace=True)
            c.tie=None    
            rn = roman.romanNumeralFromChord(c, key)
            c.addLyric(str(rn.figure)) 
            c._duration = duration.Duration(1.0)
            c.groups.append('chords')
            for pitch in c.pitches:
                c.setColor('grey', pitch)
        else:
            c.groups.append('erase')
            for pitch in c.pitches:
                c.remove(pitch)
    newScore = copy.deepcopy(score)
    newScore.append(chords)    
    return (newScore)

##################################################################################
def bassoContinuo(score):
    chords = score.chordify()
    key = score.analyze('key')
    chords.partName = "B.C."
    chords.partId = "B.C."
    chords.partAbbreviation = "B.C."
    chords._partAbbreviation = "B.C."
    
    for c in chords[chord.Chord]:
        offset = c._activeSiteStoredOffset
        if offset==int(offset):
            #print(offset) #offset by measure
            c.closedPosition(inPlace=True)
            c.tie=None    
            c._duration = duration.Duration(1.0)
            c.groups.append('chords')
            c.annotateIntervals()
            for pitch in c.pitches[1:]:
                c.remove(pitch)
                #c.setColor('red', pitch)
            c.setColor('blue', c.pitches[0])      
        else:
            c.groups.append('erase')
            for pitch in c.pitches:
                c.remove(pitch)
    newScore = copy.deepcopy(score)
    bassClef = clef.BassClef()

    #checks if pick up bar at measure 0, if not, then start with measure 1
    firstMeasure = score.measure(0)[note.Note]
    measure = 1 if len(firstMeasure)==0 else 0

    if not chords.measure(measure).clef:
        chords.measure(measure).append(bassClef)
    else:
        chords.measure(measure).replace(chords.measure(measure).clef, bassClef)
    chords.measure(measure).show('text')
    newScore.append(chords)
    return (newScore)

##################################################################################
def jsymbolic(score,extractor):
	fe2=eval('features.jSymbolic.'+extractor+'(score)')
	return (fe2.extract().vector[-1])


##################################################################################
def voiceCipher(score, measureBreak=None):
    '''
    Creates a copy of the score and iters over al pair-parts,
    adding cipher notation as lyrics into each note and modifying 
    note the duration / adding notes for the purpouse of cipher placement;
    Then proceeds to hide all but the lyrics and adds the notated part into 
    the original (copyed) part.

    TODO
        1. Contrary motion sometimes mess up inward with outward; check vlq.

        2. How to handle transpositors?

        3. on removeNotations: remove slurs and other spanner elements
          ([spanner.Slur], [spanner.Spanner]().

        4. Allow cipher to reset after any rests in any pair-parts. 

        5. Allow color notation on specific intervals based on user input selection.

        6. Return a sumary of intervals, motions and parts.
    '''

    # checks for input score conditions
    checkStream(score)

    '''
    'motionSymbol' dictionary maps each type of motion to a symbol:
      - Oblique motion uses no symbol;
      - Paralel motion uses '=';
      - Contrary motion uses '<' and '>' for outward and inward respectively;
      - Direct motion (similar motion) uses "↗" if ascending
        and "↘" for descending movement.
    '''
    
    motionSymbol = {
        "parallelMotion":           "=",
        "obliqueMotion":            "",
        "outwardContraryMotion":    "<",
        "inwardContraryMotion":     ">",
        "similarMotion": {
            "Direction.ASCENDING":  "↗",
            "Direction.DESCENDING": "↘",
            "1":  "↗",
            "-1": "↘",
            1:  "↗",
            -1: "↘"
        }
    }

    # creates an empty copy of original score
    finalScore = score.cloneEmpty()

    # builds score tree from original score
    scoreTree = tree.fromStream.asTimespans(score,flatten=True,classList=(note.Note,chord.Chord))
    
    # sets a safety number of iters for while loop
    retryCounter = len(scoreTree.allOffsets())

    # ! main algorithm
    # iter over a pair of parts
    for part1, part2 in yieldParts(score):

        # sets counter for while loop
        counter = retryCounter
        
        # creates a copy containing 'part1' part (the part into wich the cipher will be notated)  
        cipherScore = score.cloneEmpty()
        cipherScore.append(copy.deepcopy(score.parts[part1]))

        # cleans lyrics, expresions and articulations
        removeNotations(cipherScore) 

        # gets a flatten version for all notes
        cipherScoreNotes = cipherScore.flatten().notes

        # set init verticality at offset 0
        verticality = scoreTree.getVerticalityAt(0.0)
        
        # retrives original score note.Note elements at offset 0
        n1v1 = score.parts[part1][note.Note].getElementsByOffset(0.0)
        n1v2 = score.parts[part2][note.Note].getElementsByOffset(0.0)

        # also retrives note at offset 0 from flat version
        initialNote = cipherScoreNotes.getElementsByOffset(0.0)

        # if note elements exists then cipher the first harmonic interval
        if initialNote:
            if n1v1 and n1v2:
                initalInterval = str(interval.Interval(n1v1[0], n1v2[0]).generic.undirected)
                initialNote[0].lyric = initalInterval

            initialNote[0].duration.quarterLength = float(verticality.timeToNextEvent)

        # inters over all verticality objects
        verticality = verticality.nextVerticality
        while verticality is not None:
            
            # safty counter prevents infinite loop
            counter -= 1
            if counter == 0:
                print ("WARNING: Something went wrong!")
                print (f'Details: Iteration over parts ({part1}, {part2}) terminated by safty counter!')
                break
            
            # at this point, vlq objects could get exception error because of wrong inputs
            try:
                vlq = verticality.getAllVoiceLeadingQuartets(
                    includeRests=True,
                    includeNoMotion=True,
                    partPairNumbers=[(part1, part2)])
            except Exception as error:
                print ("WARNING: Error on creating voice leading object.")
                print ("Details:", error)

            # if no voice leading proceed to next verticality, else
            if vlq:

                # gets the part1 note at te current offset
                currentNote = cipherScoreNotes.getElementsByOffset(verticality.offset)

                # if exists, add cipher lyrics and adjust duration = next verticality
                if currentNote: 
                    currentNote = currentNote[0] 
                    currentNote.lyric = addLyrics(vlq[0], motionSymbol)
                    currentNote.duration.quarterLength = float(verticality.timeToNextEvent)

                # note elements doesnt exists on part1 
                # (there is a oblique movement with part 2)
                else:
                    # creates a new note using 
                    # ! THE UPPER VOICE PREVIOUS PITCH
                    # to avoid new altered notes in the staff!
                    previousOffset = verticality.offset-verticality.timeToNextEvent
                    previousNote = cipherScoreNotes.getElementsByOffset(previousOffset)

                    # if no previous note is found use initial note
                    if previousNote:
                        newNote = note.Note(previousNote[0].pitch) 
                    else:
                        newNote = note.Note(cipherScoreNotes[0].pitch)

                    # gets note measure and context offset
                    noteMeasure = vlq[0].v1n2.measureNumber
                    noteOffset = verticality.offset
                    
                    # add cipher and adjust duration
                    newNote.lyric = addLyrics(vlq[0], motionSymbol)
                    newNote.duration.quarterLength = float(verticality.timeToNextEvent)
                    newNote.offset = noteOffset

                    # insert into a flatten version of parts[0] to fit offset
                    cipherScore.parts[0].flatten().insert(noteOffset, newNote)

                    # updates flatten list 'cipherScoreNotes'
                    cipherScoreNotes = cipherScore.flatten().notes

            verticality = verticality.nextVerticality
        # while end

        # after the while loop, make notation; mark cipher part as 'hideVoice'
        #cipherScore.makeNotation(inPlace=True)
        cipherScore.addGroupForElements('hideVoice',classFilter=(note.Note,note.Rest),recurse=True)
              
        
        # add a 'cleaned' original part to the score and merges with the cipher one
        originalPart = score.parts[part1]
        removeNotations(originalPart)  
        cipherScore.append(originalPart)
        finalPart = cipherScore.partsToVoices()

        # insert finalPart into finalScore
        finalScore.insert(finalPart.parts[0])

    # after prociding with all pair-parts
    # calls make notation and hide all cipher voices
    finalScore.makeNotation(inPlace=True)
    hideVoices(finalScore)

    names = [part.partName for part in score.parts]
    for part, name in zip(finalScore.parts, names):
        part.partName = name

    # calls layout function
    if measureBreak:
        systemLayout(finalScore, measureBreak)

    return finalScore

def checkStream(score):
    '''
    Verify if the input is a proper stream, has more thant one part
    and no voices in each part'''

    if not score.isStream:
        raise Exception("No proper stream object at input")
    
    if len(score.voices) > 0:
        raise Exception("Score cannot have Voices")

    if len(score.parts) < 1:
        raise Exception("Score should have more than one Part")


def addLyrics(vlq, motionSymbol):
    '''
    Adds the armonic interval value and motion type as lyric into a note.
    Maps each motion type with a particular symbol
    using 'motionSymbol' dictionary and 'eval' function.   
    '''
  
    harmonicInterval = str(reduceInterval(vlq.vIntervals[1].generic.undirected))

    for keyExpresion in motionSymbol:
        if eval('vlq.' + keyExpresion + '()'):
            # if is not 'similarMotion' the procede
            if keyExpresion != 'similarMotion':
                return motionSymbol[keyExpresion] + harmonicInterval
            
            # else check the direction of the direct motion
            direction = vlq.hIntervals[0].direction
            return motionSymbol[keyExpresion][direction] + harmonicInterval


def reduceInterval(num):
    '''
    Reduces an armonic intervals value (integer) to an ambiuts of a 10th
    '''
    while num > 10:
        num = num - 7
    return num


def yieldParts(s):
    '''
    Yields Tuples of each pair-part combination in the score
    including a Bass-Soprano pair;
    e.g. (0,1), (1,2), (2,3), (3,0) for a SATB score.
    '''
    num_parts = len(s.parts)
    for n in range(num_parts):
        yield (n % num_parts, (n + 1) % num_parts)


def removeNotations(score):
    '''
    Removes all type of expression and articulations marks,
    lyrics and chords notations.
    '''
    for noteElement in score[note.Note]:
        noteElement.articulations = ''
        noteElement.expressions = ''
        noteElement.lyric = ''


def hideVoices(score):
    '''
    This function hide notes elements marked up as 'hideVoice',
    also removes notehead, stems, beams, accidentals and ties.
    This function its called at the end of the process over the entire score.
    '''

    def hide_notes(note):
            note._notehead = 'none'
            note._stemDirection = 'none'
            hide_accidental(note.pitch)
            hide_beams(note.beams)
            hide_tie(note.tie)

    def hide_accidental(notePitch):
        if notePitch.accidental or notePitch._accidental:
            notePitch.accidental.displayType = 'never'
            notePitch.accidental.displayStatus = False
            notePitch._accidental.displayType = 'never'
            notePitch._accidental.displayStatus = False

    def hide_beams(noteBeams):
        if noteBeams:
            noteBeams.setByNumber(1, 'stop', direction=None)

    def hide_tie(noteTie):
        if noteTie:
            noteTie.style = 'hidden'

    for objectElement in score.recurse().getElementsByGroup('hideVoice'):
        objectElement.style.hideObjectOnPrint = True

        if objectElement.isNote:
            hide_notes(objectElement)


def systemLayout(score, measureBreak):
    '''
    Creates a system layout equal to the measureBreak input.
    This is needed for better readability.
    '''
    last = score.parts.first().getElementsByClass(stream.Measure).last().number
    try:
        for n in range(0, last, measureBreak):
            score.parts[0].measure(n).insert(n, layout.SystemLayout(isNew=True))

    except Exception as error:
        print ("WARNING: Error on performing system layout.")
        print ("Details:", error)
        return score