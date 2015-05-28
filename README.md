LASA Engineering Design Quizzer
********************************
Google App Engine based project to allow people to sign in to their Google Account and take quizzes.

Students have the option of being in a class, and teachers can have up to 6 classes of 50 students each.

Additional CSS work will probably be done as time goes on, but for now this is really nice for keyboard navigation.


Instruction:
**********************************
This has been written for the Google App Engine with the Python runtime. Instructions on how to install it can be found here. `https://cloud.google.com/appengine/docs/python/`

Once that has been done, all you need to do is go into the file `quizData.tsv` located in the root directory of this project and replace the questions and answers as you wish. This application is fairly hard coded, so you currently have 6 quizzes. If you want to change that, just add more links to the end, and change `configuration.py`'s loop count. Everything else is based off of the lengths of the arrays, so you'll just need to update those locations. Once you have edited `quizData.tsv` and run `configuration.py`, you can upload the app to the Google App Engine.


TODO:
**********************************
Comment code

Clean up dead code (should be done already)

Add redirects for easier integration with other websites

Add configuration file to allow for easy edits by non-programming teachers

Add instructions
