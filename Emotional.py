import indicoio
import sys
# import nltk
# nltk.download('punkt')
import numpy
import scipy.io.wavfile
import json
from watson_developer_cloud import SpeechToTextV1
from pydub import AudioSegment

# Adding the API and importing the Vokaturi module
sys.path.append("/Users/nchao/Desktop/Yale Hacks/api")
import Vokaturi

# get file upload or text input

# Emotion analysis for text
def textAnalysis(fileName):

    # API key to access indicoio api
    indicoio.config.api_key = '06ca2da07a6fd7c7746f1d4c202bdc5a'

    # Determine whether to use inputted text or to use user uploaded file
    # userInput = open('uploads/' + fileName).read()

    # Break up text into sentences and get emotion for each individual sentence
    # tokenizedUserInput = nltk.tokenize.sent_tokenize(userInput)

    tokenizedUserInput = []
    with open ('uploads/' + fileName, "r") as myfile:
        txt = myfile.read().replace("\r\n", "\n")
        tokenizedUserInput = txt.split("\n\n")
    sentNum = 1
    # array for graphic visualization
    data1 = dict()
    data1["datasets"] = [{"name": "Anger"}, {"name": "Surprise"}, {"name": "Fear"}, {"name": "Sadness"}, {"name": "Joy"}]
    data2 = dict()
    data2["datasets"] = [{"name": "Anger"}, {"name": "Surprise"}, {"name": "Fear"}, {"name": "Sadness"}, {"name": "Joy"}]
    response = []
    for i in range(5):
        data1["datasets"][i]["data"] = []
        data1["datasets"][i]["unit"] = "Response"
        data1["datasets"][i]["type"] = "area"
        data1["datasets"][i]["valueDecimals"] = 3
        data2["datasets"][i]["data"] = []
        data2["datasets"][i]["unit"] = "Response"
        data2["datasets"][i]["type"] = "area"
        data2["datasets"][i]["valueDecimals"] = 3

    for sentence in tokenizedUserInput:
        sentence = sentence.strip()
        #print(sentence)
        vals = sentAnalysis(sentence, sentNum, False)
        response.append([sentence, (sentNum % 2), vals[0], vals[1], vals[2], vals[3], vals[4]])
        if sentNum % 2 == 0:
            for i in range(5):
                data2["datasets"][i]["data"].append(vals[i])
        else:
            for i in range(5):
                data1["datasets"][i]["data"].append(vals[i])
        sentNum += 1

    data1["xData"] = []
    data2["xData"] = []
    for i in range(len(data1["datasets"][0]["data"])):
        data1["xData"].append(i + 1)
    for i in range(len(data2["datasets"][0]["data"])):
        data2["xData"].append(i + 1)
    # Get emotion for entire passage as a whole.
    # sentAnalysis(userInput, sentNum, True)
    # Create array for graphic visualization of emotions throughout the convo
    with open('data1.json', 'w') as outfile:
        json.dump(data1, outfile)
    with open('data2.json', 'w') as outfile:
        json.dump(data2, outfile)
    # return anger, surprise, fear, sadness, joy
    # print(response)
    return data1, data2, response

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
<<<<<<< HEAD
=======
        # emoVals = list(emoDict.values())
        # return [sentence, emoVals[0]],[sentence, emoVals[1]],[sentence, emoVals[2]],[sentence, emoVals[3]],[sentence, emoVals[4]]
        return list(emoDict.values())
>>>>>>> c02cee2ea32118a09f33d949063a13d85b9f9cab

        
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

    # print("")
    # print("timestamp0 len: " + str(len(timestamps0)))
    # print("")
    # print("timestamp0:")
    # print(timestamps0)
    # print("")
    # print("timestamp1:")
    # print(timestamps1)
    # print("")
    # print("timestamp1 len: " + str(len(timestamps1)))
    # print("")
    
    # Get respective dialogue for each time stamp interval
    curr_speaker, time_index = 0, 0
    dialogue0, dialogue1, dialogue = [], [], ""
    for alternatives in jason["results"]:
        for timestamps in alternatives["alternatives"]:
            for word in timestamps["timestamps"]: #word is indexable
                if curr_speaker == 0:

                    # print("")
                    # print("word")
                    # print(word)
                    # print("")
                    # print("timestamps from dic")
                    # print(timestamps)
                    # print("")
                    # print('time_index')
                    # print(time_index)
                    # print("")

                    if time_index < len(timestamps0):
                        if word[2] > timestamps0[time_index][1]:
                            curr_speaker = 1
                            dialogue0.append(dialogue)
                            dialogue = word[0] + " "
                        else:
                            dialogue += word[0] + " "

                if curr_speaker == 1:
                    if time_index < len(timestamps1):
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
    song = AudioSegment.from_wav("uploads/" + fileName) 
    index = 0
    fileList0, fileList1 = [], []
    for interval in timestamps0:
        chunk = song[interval[0]*1000 : interval[1]*1000]
        name = fileName[0:len(fileName)-4] + "_s0_" + str(index) + ".wav"
        chunk.export(name, format = "wav")
        fileList0.append(name)
        index += 1
    index = 0
    for interval in timestamps1:
        chunk = song[interval[0]*1000 : interval[1]*1000]
        name = fileName[0:len(fileName)-4] + "_s1_" + str(index) + ".wav"
        chunk.export(name, format = "wav")
        fileList1.append(name)
        index += 1

   # print("time to DUELELELELELEELELELLELEL")





                ######### YILING'S STUFF ########
                # emoVals = list(emoDict.values())
                # return [sentence, emoVals[0]],[sentence, emoVals[1]],[sentence, emoVals[2]],[sentence, emoVals[3]],[sentence, emoVals[4]]
                # return list(emoDict.values())

                # # Emotion analysis for voice audio --> Might need to split voice audio in sentences too!?!?!?!?!
                # def voiceAnalysis():
                # >>>>>>> 34eba002c10335b7d6cb453c50943471bfee25b4
                #################################





    # dialogue0 & dialogue1 = ["text", "text", ...]
    # fileList0 & fileList1 = []

    # Loop through each audio file in fileList0 and fileList1 to analyze with vokaturi

    # Get emotion probabilities for each individual voice file and save in person0_emotions & person1_emotions
    person0_emotions = []
    for i in range(len(fileList0)):
        audioDict = callVokaturi(fileList0[i])
        sentenceDict = sentEmotion(dialogue0[i])

        #probabilities
        joy = (audioDict["Happy"] + sentenceDict["joy"])/2
        sadness = (audioDict["Sad"] + sentenceDict["sadness"])/2
        neutral = (audioDict["Neutral"] + sentenceDict["neutral"])/2
        fear = (audioDict["Fear"] + sentenceDict["fear"])/2
        anger = (audioDict["Angry"] + sentenceDict["anger"])/2
        person0_emotions.append([anger, neutral, fear, sadness, joy])

    person1_emotions = []
    for i in range(len(fileList1)):
        audioDict = callVokaturi(fileList1[i])
        sentenceDict = sentEmotion(dialogue1[i])

        #probabilities
        joy = (audioDict["Happy"] + sentenceDict["joy"])/2
        sadness = (audioDict["Sad"] + sentenceDict["sadness"])/2
        neutral = (audioDict["Neutral"] + sentenceDict["neutral"])/2
        fear = (audioDict["Fear"] + sentenceDict["fear"])/2
        anger = (audioDict["Angry"] + sentenceDict["anger"])/2
        person1_emotions.append([anger, neutral, fear, sadness, joy])

    response = []
    for i in range(len(dialogue0)):
        anger0, anger1 = person0_emotions[i][0], person1_emotions[i][0]
        neutral0, neutral1 = person0_emotions[i][1], person1_emotions[i][1]
        fear0, fear1 = person0_emotions[i][2], person1_emotions[i][2]
        sadness0, sadness1 = person0_emotions[i][3], person1_emotions[i][3]
        joy0, joy1 = person0_emotions[i][4], person1_emotions[i][4]

        response.append([dialogue0[i], 1, anger0, neutral0, fear0, sadness0, joy0])
        response.append([dialogue1[i], 0, anger1, neutral1, fear1, sadness1, joy1])

    data1 = voiceHelper(person0_emotions)
    data2 = voiceHelper(person1_emotions)

    return data1, data2, response

    # person0_emotions & person1_emotions are list of each person's emotions matching up to the dialogue they say
    # in dialogue0 and dialogue1.

def voiceHelper(personEmotions):
    # array for graphic visualization
    data1 = dict()
    data1["datasets"] = [{"name": "Anger"}, {"name": "Neutral"}, {"name": "Fear"}, {"name": "Sadness"}, {"name": "Joy"}] 
    for i in range(5):
        data1["datasets"][i]["data"] = []
        data1["datasets"][i]["unit"] = "Response"
        data1["datasets"][i]["type"] = "area"
        data1["datasets"][i]["valueDecimals"] = 3

    for j in range(len(personEmotions)):
        vals = personEmotions[j]
        for i in range(5):
            data1["datasets"][i]["data"].append(vals[i])

    data1["xData"] = []
    for i in range(len(data1["datasets"][0]["data"])):
        data1["xData"].append(i + 1)

    # Create array for graphic visualization of emotions throughout the convo
    with open('data1.json', 'w') as outfile:
        json.dump(data1, outfile)
    # return anger, surprise, fear, sadness, joy
    #print(response)
    return data1



# Getting a dictionary with emotion probabilities for a voice file
def callVokaturi(fileName):

    # Loading Vokaturi Mac
    Vokaturi.load("/Users/nchao/Desktop/Yale Hacks/lib/Vokaturi_mac.so")

    # Reading sound files (.wav)
    file_name = "/Users/nchao/Desktop/Yale Hacks/" + fileName
    (sample_rate, samples) = scipy.io.wavfile.read(file_name)

    # Allocating Vokaturi sample array
    buffer_length = len(samples)
    c_buffer = Vokaturi.SampleArrayC(buffer_length)
    if samples.ndim == 1:
        c_buffer[:] = samples[:] / 32768.0  # mono
    else:
        c_buffer[:] = 0.5*(samples[:,0]+0.0+samples[:,1]) / 32768.0 # stereo

    # Creating VokaturiVoice and filling it with voice sample
    voice = Vokaturi.Voice(sample_rate, buffer_length)
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
    indicoio.config.api_key = '06ca2da07a6fd7c7746f1d4c202bdc5a'
    emoDict = indicoio.emotion(sentence)
    emoDict["neutral"] = emoDict["surprise"]
    # Determine if the overall emotion is neutral or not
    # if max(emoDict.values()) - min(emoDict.values()) > 0.1:
    #     neutralEmoDict = {}
    #     neutralEmoDict["neutral"] = emoDict["surprise"] + 0.85*emoDict["fear"] + 0.85*emoDict["anger"] + 0.85*emoDict["joy"] + 0.85*emoDict["sadness"]
    #     neutralEmoDict["fear"] = 0.15*emoDict["fear"]
    #     neutralEmoDict["anger"] = 0.15*emoDict["anger"]
    #     neutralEmoDict["joy"] = 0.15*emoDict["joy"]
    #     neutralEmoDict["sadness"] = 0.15*emoDict["sadness"]
    #     return neutralEmoDict
    return emoDict



def main(fileName):
    # To run the text analysis
    if fileName[len(fileName)-3:] is 'txt':
        # print("Text Analysis:")
        # print("")
        data1, data2, response = textAnalysis(fileName)
        return data1, data2, response
    else:
        data1, data2, response = voiceAnalysis(fileName)
        return data1, data2, response

# main()
