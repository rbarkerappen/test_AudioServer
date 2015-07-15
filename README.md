Audio Server
============
When we move transcription or other audio based work to AWS, the application won't be able to access the audio anymore. It is possible that eventually we store the audio on AWS too, but some clients will not agree to storing their audio on Amazon.

This application is a small audio server which can run on our servers and can be used to serve MP3s, Oggs and waveforms.

To test out the app:
1. Setup the enironment by sourcing setenv.sh
2. Run the app.py
3. Run the various demos in demo.py which demonstrate usage

# Triage #
There is also a small triage-style app (triage.py) included. Basically, if we get to a point where each of our audio storage servers have the same setup, installed packages, etc. and produce consistent output, we could setup the main audio server to run on each storage server then use the triage app to redirect the request to the one which hosts the audio. This should processing the audio faster as the file will be local to the server.

Note: the contents of the utils/ folder should probably be stored in our utilities repo.
