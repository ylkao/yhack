import indicoio
import sys
# import nltk
# nltk.download('punkt')
import numpy
import scipy.io.wavfile
import json


# get file upload or text input

# Emotion analysis for text
def textAnalysis(fileName):

    # API key to access indicoio api
    indicoio.config.api_key = '06ca2da07a6fd7c7746f1d4c202bdc5a'

    # Determine whether to use inputted text or to use user uploaded file
    userInput = open('uploads/' + fileName).read()

    # Break up text into sentences and get emotion for each individual sentence
    tokenizedUserInput = nltk.tokenize.sent_tokenize(userInput)
    sentNum = 1
    # array for graphic visualization
    """ anger = []
    surprise = []
    fear = []
    sadness = []
    joy = [] """
    data = dict()
    data["datasets"] = [{"name": "Anger"}, {"name": "Surprise"}, {"name": "Fear"}, {"name": "Sadness"}, {"name": "Joy"}] 
    for i in range(5):
        data["datasets"][i]["data"] = []
        data["datasets"][i]["unit"] = "Response"
        data["datasets"][i]["type"] = "area"
        data["datasets"][i]["valueDecimals"] = 0
   for sentence in tokenizedUserInput:
        if sentNum % 2 == 0:
            data["datasets"][0]
        a, b, c, d, e = sentAnalysis(sentence, sentNum, False)
        anger.append(a)
        surprise.append(b)
        fear.append(c)
        sadness.append(d)
        joy.append(e)
        sentNum += 1
    data["xData"] = []
    for i in range(len(tokenizedUserInput)):
        data["xData"].append(i + 1)

    # Get emotion for entire passage as a whole.
    sentAnalysis(userInput, sentNum, True)
    # Create array for graphic visualization of emotions throughout the convo
    # with open('graph.json', 'w') as outfile:
    #     json.dump(graph, outfile)
    # return anger, surprise, fear, sadness, joy

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
            # print(sentence)
        emoVals = emoDict.values()
        return [sentence, emoVals[0]],[sentence, emoVals[1]],[sentence, emoVals[2]],[sentence, emoVals[3]],[sentence, emoVals[4]]
        
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
        print("Neutral: %.3f" % emotionProbabilities.neutrality)
        print("Happy: %.3f" % emotionProbabilities.happiness)
        print("Sad: %.3f" % emotionProbabilities.sadness)
        print("Angry: %.3f" % emotionProbabilities.anger)
        print("Fear: %.3f" % emotionProbabilities.fear)

    voice.destroy()

def main(fileName):
    # To run the text analysis
    print("Text Analysis:")
    print("")
    anger, surprise, fear, sadness, joy = textAnalysis(fileName)

    # To run the voice analysis
    # print("Voice Analysis:")
    # print("")
    #voiceAnalysis()

    return anger, surprise, fear, sadness, joy

# main()