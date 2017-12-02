/*
	MeasureWav.c
	public-domain sample code by Vokaturi, 2017-07-14

	A program that calls the Vokaturi API
	to report the average emotion probabilities
    in a prerecorded WAV file.
*/

#include <math.h>
#include "WavFile.h"

int main (int argc, const char * argv[]) {
	if (argc < 2) {
		printf ("Usage: MeasureWav [soundfilename.wav ...]\n");
		exit (1);
	}
	printf ("**********\nWAV files analyzed with:\n%s\n**********\n",
		Vokaturi_versionAndLicense ());
	for (int ifile = 1; ifile < argc; ifile ++) {
		const char *fileName = argv [ifile];

		printf ("\nEmotion analysis of WAV file %s:\n", fileName);
		VokaturiWavFile wavFile;
		VokaturiWavFile_open (fileName, & wavFile);
		if (! VokaturiWavFile_valid (& wavFile)) {
			fprintf (stderr, "Error: WAV file not analyzed.\n");
			exit (1);
		}

		VokaturiVoice voice = VokaturiVoice_create (
			wavFile.samplingFrequency,
			wavFile.numberOfSamples
		);

		VokaturiWavFile_fillVoice (& wavFile, voice,
			0,   // the only or left channel
			0,   // starting from the first sample
			wavFile.numberOfSamples   // all samples
		);

		VokaturiQuality quality;
		VokaturiEmotionProbabilities emotionProbabilities;
		VokaturiVoice_extract (voice, & quality, & emotionProbabilities);

		if (quality.valid) {
			printf ("Neutrality %.3f\n", emotionProbabilities.neutrality);
			printf ("Happiness %.3f\n", emotionProbabilities.happiness);
			printf ("Sadness %.3f\n", emotionProbabilities.sadness);
			printf ("Anger %.3f\n", emotionProbabilities.anger);
			printf ("Fear %.3f\n", emotionProbabilities.fear);
		} else {
			printf ("Not enough sonorancy to determine emotions\n");
		}

		VokaturiVoice_destroy (voice);
		VokaturiWavFile_clear (& wavFile);
	}
}
