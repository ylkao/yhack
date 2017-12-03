import indicoio
import sys
import nltk
nltk.download('punkt')
import numpy
import scipy.io.wavfile
import json
from watson_developer_cloud import SpeechToTextV1
from pydub import AudioSegment

# get file upload or text input

# Emotion analysis for text
def textAnalysis(fileName):

    # API key to access indicoio api
    indicoio.config.api_key = '06ca2da07a6fd7c7746f1d4c202bdc5a'

    # Determine whether to use inputted text or to use user uploaded file
    userInput = open('uploads/' + fileName).read()

    # To test neutral case
    # userInput = "Hello."

    # To test else case
    # userInput = "Mai nam i\'z Mr. Gabe, I am da boi, on Interwebz, Who breeng u joy.\
    #             Wth all mai barkz, an sniffs an sneeze, I do teh sing, I am da meemz.\
    #             Altho am nao, with starry light, up in heavan, I sleepng tight.\
    #             So plz no cri, Remember mee, as happy boi, I'll always be."

#     userInput = "Silence of the Lambs (1991) DR. LECTER Oh, Officer Starling... do you think you can \
#     dissect me with this bluntlittle tool? CLARICE No. I only hoped that your knowledge \
#     -Suddenly he whips the tray back at her, with a metallic CLANG that makes her start. His voice remains a pleasant purr. (CONT'D) You're sooo ambitious, aren't you...? You know what you look like tome, with your good bag and your cheap shoes? You look like a rube. Awell-scrubbed, hustling rube with a little taste... Good nutrition hasgiven you some length of bone, but you're not more than one generationfrom poor white trash, are you - Officer Starling...? That accentyou're trying so desperately to shed - pure West Virginia. What wasyour father, dear? Was he a coal miner? Did he stink of the lamp...? \
#     And oh, how quickly the boys found you! All those tedious, sticky fumblings, in the back seats of cars, \
#     while you could only dream of getting out. \
#     Getting anywhere - yes? Getting all the way - to theF...B...I.His every word has struck her \
#     like a tiny, precise dart. But shesquares her jaw and won't give ground. CLARICE \
#     You see a lot, Dr. Lecter. But are you strong enough to point thathigh-powered perception at yourself? \
#     How about it...? Look at yourselfand write down the truth.(she slams the tray back at him)Or maybe you're afraid to. \
#     DR. LECTERYou're a tough one, aren't you? \
# CLARICE Reasonably so. Yes. DR. LECTER And you'd hate to think you were common. \
# My, wouldn't that sting! Wellyou're far from common, Officer Starling. All you have is the fear ofit. \
# (beat)Now please excuse me. Good day. CLARICE And the questionnaire...? DR. LECTER \
# A census taker once tried to test me. I ate his liver with some favabeans and a nice chianti... \
# Fly back to school, little Starling."

    # Break up text into sentences and get emotion for each individual sentence
    tokenizedUserInput = nltk.tokenize.sent_tokenize(userInput)
    sentNum = 1
    # array for graphic visualization
    anger = []
    surprise = []
    fear = []
    sadness = []
    joy = []
    for sentence in tokenizedUserInput:
        a, b, c, d, e = sentAnalysis(sentence, sentNum, False)
        anger.append(a)
        surprise.append(b)
        fear.append(c)
        sadness.append(d)
        joy.append(e)
        sentNum += 1

    # Get emotion for entire passage as a whole.
    sentAnalysis(userInput, sentNum, True)
    # Create array for graphic visualization of emotions throughout the convo
    # with open('graph.json', 'w') as outfile:
    #     json.dump(graph, outfile)
    return anger, surprise, fear, sadness, joy

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

    emoVals = list(emoDict.values())
    return [sentence, emoVals[0]],[sentence, emoVals[1]],[sentence, emoVals[2]],[sentence, emoVals[3]],[sentence, emoVals[4]]

        # # Send result back to web app, but just printing right now for testing purposes
        # if entireText:
        #     print("")
        #     if isNeutral:
        #         print("Overall Text Emotion: " + "neutral")
        #         print("")
        #     else:
        #         print("Overall Text Emotion: " + ", ".join(emotions))
        #         print("")
        # else:
        #     if isNeutral:
        #         print("Sentence " + str(sentNum) + " Emotion: " + "neutral")
        #     else:
        #         print("Sentence " + str(sentNum) + " Emotion: " + ", ".join(emotions))
            # print(sentence)
        
# Emotion analysis for voice audio --> Might need to split voice audio in sentences too!?!?!?!?! 
def voiceAnalysis(fileName):

    # Use IBM Watson to split audio file by speakers
    IBM_USERNAME = "b3d74b00-edb2-4069-8d43-0d09259d1ba6"
    IBM_PASSWORD = "lDNJYt4ta0Vd"

    stt = SpeechToTextV1(username=IBM_USERNAME, password=IBM_PASSWORD)
    audioFile = open('uploads/' + fileName, "rb")

    with open('transcript_result.json', 'w') as outfile:
        result = stt.recognize(audioFile, content_type="audio/wav", continuous=True,
                                timestamps=True, max_alternatives=1, speaker_labels=True)
        json.dump(result, outfile, indent=2)

    # Open json file
    jason = json.load(open('transcript_result.json'))

    # Get time stamps for each person's resonse
    curr_speaker = 0
    timestamps0, timestamps1, dialogue = [], [],[]
    for dictionary in jason["speaker_labels"]:
        if len(dialogue) == 0:
            dialogue.append(dictionary["from"])
        if dictionary["speaker"] != curr_speaker:
            dialogue.append(dictionary["from"])
            if curr_speaker == 0:
                timestamps0.append(dialogue)
            else:
                timestamps1.append(dialogue)
            dialogue = [dictionary["from"]]
            curr_speaker = dictionary["speaker"]

    print("timestamp0 len: " + str(len(timestamps0)))
    print("tiemstamp1 len: " + str(len(timestamps1)))
    
    # Get respective dialogue for each time stamp interval
    curr_speaker, time_index = 0, 0
    dialogue0, dialogue1, dialogue = [], [], ""
    for alternatives in jason["results"]:
        for timestamps in alternatives:
            for word in timestamps: #word is indexable
                if curr_speaker == 0:
                    if word[2] > timestamps0[time_index][1]:
                        curr_speaker = 1
                        dialogue0.append(dialogue)
                        dialogue = word[0] + " "
                    else:
                        dialogue += word[0] + " "
                if curr_speaker == 1:
                    if word[2] > timestamps1[time_index][1]:
                        curr_speaker = 0
                        dialogue1.append(dialogue)
                        dialogue = word[0] + " "
                        time_index += 1
                    else:
                        dialogue += word[0] + " "

    # timestamps0, timestamps1 = [[start, end], [start, end]...]
    # dialogue0 & dialogue1 = ["text", "text", ...]

    #need split times in milliseconds
    song = AudioSegment.from_wav(fileName) 
    index = 0
    fileList0, fileList1 = [], []
    for interval in timestamps0:
        chunk = song[interval[0]*1000 : interval[1]*1000]
        name = "uploads/" + fileName + "_s0_" + str(index) + ".wav"
        chunk.export(name, format = "wav")
        fileList0.append(name)
        index += 1
    index = 0
    for interval in timestamps1:
        chunk = song[interval[0]*1000 : interval[1]*1000]
        name = "uploads/" + fileName + "_s1_" + str(index) + ".wav"
        chunk.export(name, format = "wav")
        fileList1.append(name)
        index += 1

    # dialogue0 & dialogue1 = ["text", "text", ...]
    # fileList0 & fileList1 = []

    # Loop through each audio file in fileList0 and fileList1 to analyze with vokaturi

    # Adding the API and importing the Vokaturi module
    sys.path.append("/Users/nchao/Desktop/Yale Hacks/api")
    import Vokaturi

    # Loading Vokaturi Mac
    Vokaturi.load("/Users/nchao/Desktop/Yale Hacks/lib/Vokaturi_mac.so")

    # Get emotion probabilities for each individual voice file and save in person0_emotions & person1_emotions
    person0_emotions = []
    for i in range(len(fileList0)):
        audioDict = callVokaturi(fileList0[i])
        sentenceDict = sentEmotion(dialogue0[i])

        #probabilities
        joy = avg(audioDict["Happy"] + sentenceDict["Joy"])
        sadness = avg(audioDict["Sad"] + sentenceDict["Sadness"])
        neutral = avg(audioDict["Neutral"] + sentenceDict["Neutral"])
        fear = avg(audioDict["Fear"] + sentenceDict["Fear"])
        anger = avg(audioDict["Angry"] + sentenceDict["Anger"])
        person0_emotions.append([neutral, joy, sadness, fear, anger])

    person1_emotions = []
    for i in range(len(fileList1)):
        audioDict = callVokaturi(fileList1[i])
        sentenceDict = sentEmotion(dialogue1[i])

        #probabilities
        joy = avg(audioDict["Happy"] + sentenceDict["Joy"])
        sadness = avg(audioDict["Sad"] + sentenceDict["Sadness"])
        neutral = avg(audioDict["Neutral"] + sentenceDict["Neutral"])
        fear = avg(audioDict["Fear"] + sentenceDict["Fear"])
        anger = avg(audioDict["Angry"] + sentenceDict["Anger"])
        person1_emotions.append([neutral, joy, sadness, fear, anger])

    # person0_emotions & person1_emotions are list of each person's emotions matching up to the dialogue they say
    # in dialogue0 and dialogue1.

    print("Person 0 Emotions:")
    print("")
    print(person0_emotions)
    print("")
    print("Person 1 Emotions:")
    print("")
    print(person1_emotions)

# Getting a dictionary with emotion probabilities for a voice file
def callVokaturi(fileName):

    # Reading sound files (.wav)
    file_name = "/Users/nchao/Desktop/Yale Hacks/uploads/" + fileName
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

    # Extracting emotions from Vokaturi
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

    voice.destroy()
    return emoDict

def sentEmotion(sentence): 

    # Determine which emotion(s) is/are most represented in the text
    emoDict = indicoio.emotion(sentence)

    # Determine if the overall emotion is neutral or not
    if max(emoDict.values()) - min(emoDict.values()) > 0.1:
        neutralEmoDict = {}
        neutralEmoDict["Neutral"] = emoDict["Surprise"] + 0.85*emoDict["Fear"] + 0.85*emoDict["Anger"] + 0.85*emoDict["Joy"] + 0.85*emoDict["Sadness"]
        neutralEmoDict["Fear"] = 0.15*emoDict["Fear"]
        neutralEmoDict["Anger"] = 0.15*emoDict["Anger"]
        neutralEmoDict["Joy"] = 0.15*emoDict["Joy"]
        neutralEmoDict["Sadness"] = 0.15*emoDict["Sadness"]
        return neutralEmoDict
    return emoDict

def main(fileName, fileType):

    if fileType == "txt":
        # To run the text analysis
        anger, surprise, fear, sadness, joy = textAnalysis(fileName)
        return anger, surprise, fear, sadness, joy
    else:
        # To run the voice analysis
        print("Voice Analysis:")
        print("")
        voiceAnalysis(fileName)

    # return anger, surprise, fear, sadness, joy

# main()