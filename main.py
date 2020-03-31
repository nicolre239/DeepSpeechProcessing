import moviepy.editor as mp
import glob
import csv
import time
import sys
import os

#lastFileName = [-1]
lastFileName = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
globalCounter = 0
totalDurationMs = 0

def incName(position):
    global  lastFileName
    alphabetBase = 25

    if lastFileName[position] < alphabetBase:
        lastFileName[position] = lastFileName[position] + 1
        return 0
    elif position != 0:
        lastFileName[position] = 0
        return incName(position - 1)
    else:
        for i in range(len(lastFileName)):
            lastFileName[i] = 0

        lastFileName.insert(0, 0)
        return 0

def getName():
    global lastFileName

    incName(len(lastFileName) - 1)

    name = ''
    for i in range (len(lastFileName)):
        name = name +  chr(lastFileName[i] + 97)

    return name

def getTimings (timeString):
    timeArray = [0, 0, 0, 0]
    shiftInMs = 135

    beginTimeArray = timeString.split(':')
    #print(beginTimeArray)

    timeArray[0] = int(beginTimeArray[0])
    timeArray[1] = int(beginTimeArray[1])

    secMs = str(beginTimeArray[2]).split('.')
    timeArray[2] = int(secMs[0])
    timeArray[3] = int(secMs[1])

    timeArray[3] = timeArray[3] + shiftInMs

    if timeArray[3] > 999:
        timeArray[3] = timeArray[3] % 1000
        timeArray[2] = timeArray[2] + 1

        if timeArray[2] > 60:
            timeArray[2] = timeArray[2] % 60
            timeArray[1] = timeArray[1] + 1

            if timeArray[1] > 60:
                timeArray[1] = timeArray[1] % 60
                timeArray[0] = timeArray[0] + 1

    return timeArray

#def writeRow():


def cutFile (i, book):
    mp4 = glob.glob(book + 'audio/' + str(i) + '.mp4')
    subtitles = glob.glob(book + 'text/subtitles_final_' + str(i) + '.txt')
    #print (mp4)
    #print(subtitles)

    subtitles_file = open (subtitles[0], 'r')

    while True:
        beginTime = subtitles_file.readline()
        text = subtitles_file.readline().replace("\n", "").replace("\t", "")
        endTime = subtitles_file.readline()
        emptyLine = subtitles_file.readline()

        if not beginTime or not text or not endTime:
            break;

        beginTimeArray = getTimings(beginTime)
        endTimeArray = getTimings(endTime)

        #filename = '0'
        try:
            filename = cut(mp4, beginTimeArray, endTimeArray)
        except OSError or BrokenPipeError:
            #logfile = open('logfile.txt', 'a')
            #logfile.write('\n#\n#ERROR:\n' + filename + '\n#\n')
            #logfile.close()
            continue

        if filename != '0':
            global globalCounter
            if globalCounter < 3:
                file = open('./cutted/train.tsv', 'a', newline='')
            elif globalCounter < 4:
                file = open('./cutted/dev.tsv', 'a', newline='')
            else:
                file = open('./cutted/test.tsv', 'a', newline='')

            tsv_writer = csv.writer(file, delimiter = '\t')
            tsv_writer.writerow([filename + '.mp3', text])
            file.close()

            globalCounter = (globalCounter + 1) % 5
        else:
            logfile = open('logfile.txt', 'a')

            logfile.write("\n\nCut declined cause of timing\n")
            logfile.write(beginTime)
            logfile.write(text + '\n')
            logfile.write(endTime + '\n')

            logfile.close()
            continue




def cut (mp4, beginTime, endTime):
    global totalDurationMs
    mp4_file = mp4[0]

    clip = mp.VideoFileClip(mp4_file)

    beginMs = beginTime[3] + beginTime[2] * 1000 + beginTime[1] * 60 * 1000 + beginTime[0] * 3600 * 1000
    endMs = endTime[3] + endTime[2] * 1000 + endTime[1] * 60 * 1000 + endTime[0] * 3600 * 1000

    #(beginTime)
    #print(endTime)
    if (endMs - beginMs > 1000):
        totalDurationMs = totalDurationMs + (endMs - beginMs)

        beginTimeString = str(beginTime[0]) + ':' + str(beginTime[1]) + ':' + str(beginTime[2]) + '.'
        if beginTime[3] < 10:
            beginTimeString = beginTimeString + '00'
        elif beginTime[3] < 100:
            beginTimeString = beginTimeString + '0'
        beginTimeString = beginTimeString + str(beginTime[3])

        endTimeString = str(endTime[0]) + ':' + str(endTime[1]) + ':' + str(endTime[2]) + '.'
        if endTime[3] < 10:
            endTimeString = endTimeString + '00'
        elif endTime[3] < 100:
            endTimeString = endTimeString + '0'
        endTimeString = endTimeString + str(endTime[3])

        #print(beginTimeString)
        #print(endTimeString)
        subclip = clip.subclip(beginTimeString, endTimeString)

        filename = getName()
        #print(r"./cutted/clips/" + filename + ".mp3")
        subclip.audio.write_audiofile(r"./cutted/clips/" + filename + ".mp3",  verbose=False, logger=None)
        #print('afterwrite')
        #clip = mp.AudioFileClip('./cutted/clips/' + filename + '.mp3')
        #print(clip.duration)
        #print(subclip.duration)
        #print ('beforeclose')
        clip.close()
        #print ('afterclose')
        return filename
    else:
        #print('\nClip is too short\n')
        return '0'


def main():
    global lastFileName
    global totalDurationMs

    try:
        if (int(sys.argv[1]) > 25) or (int(sys.argv[1]) < 0) or (int(sys.argv[2]) < 0) or (int(sys.argv[2]) > 25):
            print("WRONG COMMAND LINE ARGUMENT")
            return 0
        else:
            try:
                os.mkdir('./cutted')
                os.mkdir('./cutted/clips/')
            except FileExistsError:
                print('Directory already exsists')
			 
            lastFileName[0] = int(sys.argv[1])
            lastFileName[1] = int(sys.argv[2])
            start_time = time.time()
            books = glob.glob('./resources/*/')

            file = open('./cutted/train.tsv', 'w', newline='')
            tsv_writer = csv.writer(file, delimiter='\t')
            tsv_writer.writerow(['path', 'sentence'])
            file.close()

            file = open('./cutted/dev.tsv', 'w', newline='')
            tsv_writer = csv.writer(file, delimiter='\t')
            tsv_writer.writerow(['path', 'sentence'])
            file.close()

            file = open('./cutted/test.tsv', 'w', newline='')
            tsv_writer = csv.writer(file, delimiter='\t')
            tsv_writer.writerow(['path', 'sentence'])
            file.close()

            file = open('logfile.txt', 'w')
            file.close()

            for book in books:
                partsNumber = len(glob.glob(book + 'audio/*.mp4'))


                logfile = open('logfile.txt', 'a')
                logfile.write('\n******\nBOOK ' + book + '\n*\n*\n*')
                print('\n******\nBOOK ' + book + '\n*\n*\n*')
                logfile.close()

                for i in range(1, partsNumber + 1):
                    #start_time = time.time()
                    totalDurationMs = 0
                    logfile = open('logfile.txt', 'a')
                    logfile.write('\n\nWorking with part %d out of %d' % (i, partsNumber))
                    logfile.close()
                    print('\n\nWorking with part %d out of %d' % (i, partsNumber))
                    cutFile(i, book)

                    logfile = open('logfile.txt', 'a')
                    logfile.write('Total cuts time: %d:%d:%d' % (totalDurationMs // 3600000, totalDurationMs % 3600000 // 60000, totalDurationMs % 3600000 % 60000 // 1000))
                    logfile.close()
                    #print("--- %s seconds ---" % (time.time() - start_time))
    except IndexError:
        print("WRONG ARGUMENTS NUMBER. 2 ARGUMENTS REQUIRED")
        return 0

        print("--- %s seconds ---" % (time.time() - start_time))
        logfile.open('logfile.txt', 'a')
        logfile.write("--- %s seconds ---" % (time.time() - start_time))
        logfile.close()
if __name__ == '__main__':
    main()