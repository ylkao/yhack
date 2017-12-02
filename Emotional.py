import indicoio
import sys
import nltk
import numpy
import scipy.io.wavfile


# Emotion analysis for text
def textAnalysis():

    # API key to access indicoio api
    indicoio.config.api_key = '06ca2da07a6fd7c7746f1d4c202bdc5a'

    # Determine whether to use inputted text or to use user uploaded file
    # userInput = sys.stdin.readlines()                                     ----> need to figure out right way to read lines/get file
    # if userInput == none:
    # userInput = # get the uploaded file and read them

    # To test neutral case
    # userInput = "Hello."

    # To test else case
    userInput = "Mai nam iz Gabe, I am da boi, on Interwebz, Who breeng u joy.\
                Wth all mai barkz, an sniffs an sneeze, I do teh sing, I am da meemz.\
                Altho am nao, with starry light, up in heavan, I sleepng tight.\
                So plz no cri, Remember mee, as happy boi, I'll always be."

    # Break up text into sentences and get emotion for each individual sentence
    tokenizedUserInput = nltk.tokenize.sent_tokenize(userInput)
    sentNum = 1
    for sentence in tokenizedUserInput:
        sentAnalysis(sentence, sentNum, False)
        sentNum += 1

    # Get emotion for entire passage as a whole.
    sentAnalysis(userInput, sentNum, True)

# Helper function to get emotion of a single sentence
def sentAnalysis(sentence, sentNum, entireText):

    # Determine which emotion(s) is/are most represented in the text
        emoDict = indicoio.emotion(sentence)
        sortedVals = sorted(emoDict.values())[::-1]
        isNeutral = True

        # Determine if the overall emotion is neutral or not
        if max(sortedVals) - min(sortedVals) > 0.1:
            isNeutral = False
            stdDev = numpy.std(sortedVals)
            emotions = []
            for percentage in sortedVals:
                if percentage > abs(max(sortedVals) - 1.5 * stdDev):
                    emotions += [key for key, val in emoDict.items() if val == percentage]

        # Send result back to web app, but just printing right now for testing purposes
        if entireText:
            print("")
            if isNeutral:
                print("Overall Text Emotion: " + "neutral")
                print("")
            else:
                print("Overall Text Emotion: " + ", ".join(emotions))
                print("")
        else:
            if isNeutral:
                print("Sentence " + str(sentNum) + " Emotion: " + "neutral")
            else:
                print("Sentence " + str(sentNum) + " Emotion: " + ", ".join(emotions))
        
# Emotion analysis for voice audio --> Might need to split voice audio in sentences too!?!?!?!?! 
def voiceAnalysis():

    # Adding the API and importing the Vokaturi module
    sys.path.append("/Users/nchao/Desktop/Yale Hacks/api")
    import Vokaturi

    # Loading Vokaturi Mac
    Vokaturi.load("/Users/nchao/Desktop/Yale Hacks/lib/Vokaturi_mac.so")

    # Reading sound files (.wav)
    file_name = "/Users/nchao/Desktop/Yale Hacks/examples/hello.wav" #sys.argv[1] ---> Need to figure out where downloaded sound files will be after upload
    (sample_rate, samples) = scipy.io.wavfile.read(file_name)

    # Allocating Vokaturi sample array
    buffer_length = len(samples)
    c_buffer = Vokaturi.SampleArrayC(buffer_length)
    if samples.ndim == 1:
        c_buffer[:] = samples[:] / 32768.0  # mono
    else:
        c_buffer[:] = 0.5*(samples[:,0]+0.0+samples[:,1]) / 32768.0 # stereo

    # Creating VokaturiVoice and filling it with voice sample
    voice = Vokaturi.Voice (sample_rate, buffer_length)
    voice.fill(buffer_length, c_buffer)

    # Extracting emotions from VokaturiVoice
    quality = Vokaturi.Quality()
    emotionProbabilities = Vokaturi.EmotionProbabilities()
    voice.extract(quality, emotionProbabilities)
    emoDict = {"Neutral" : emotionProbabilities.neutrality, "Happy" : emotionProbabilities.happiness,
                "Sad" : emotionProbabilities.sadness, "Angry" : emotionProbabilities.anger, 
                "Fear" : emotionProbabilities.fear}

    # Finding main emotion in voice file
    sortedVals = sorted(emoDict.values())[::-1]
    stdDev = numpy.std(sortedVals)
    emotions = []
    for percentage in sortedVals:
        if percentage > abs(max(sortedVals) - 1.5 * stdDev):
            emotions += [key for key, val in emoDict.items() if val == percentage]

    # Send result back to web app, but printing it ou for testing purposes
    print("Overall Speech Emotion: " + ", ".join(emotions))

    # Printing emotion percentages for testing purposes
    if quality.valid:
        print("")
        print("Exact probabilities:")
        print("  (ಠ_ಠ)  Neutral: %.3f" % emotionProbabilities.neutrality)
        print("  (◕‿◕)  Happy: %.3f" % emotionProbabilities.happiness)
        print("  (ಥ_ಥ)  Sad: %.3f" % emotionProbabilities.sadness)
        print("ヽ(ಠ_ಠ)ノ Angry: %.3f" % emotionProbabilities.anger)
        print("  (⊙﹏⊙)  Fear: %.3f" % emotionProbabilities.fear)

    voice.destroy()

# To run the text analysis
print("Text Analysis:")
print("")
textAnalysis()

# To run the voice analysis
print("Voice Analysis:")
print("")
voiceAnalysis()