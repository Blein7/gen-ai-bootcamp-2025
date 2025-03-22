### Technical Specs

### Initialization Steps
When the app first initilizes needs to do the following:
Fetch from the get localhost:5000/api/groups/:id/raw, this will return a collection of words in a  json structure. It will have japanese words with their english translation. We need to store this collection of words in memory.


## Page States

Page states describes the state the single page application should behave from a user's perspective
## Setup State
When a user first starts the app
The user will then see a button to " Generate sentence". When they press the button, the app will generate a sentence using the sentence generator LLM, and the state will move to Practice state

## Practice State
When a user is in the Practice state
The user will see an english sentence. They will also see an upload field under the english sentence. They will see a button called "submit for review". When they press the submit for review button an uploaded image will be passed to the grading system and then will transition to the review state
## Review State
When a user is in the review state. The user will still see the english sentence. The upload field will be gone.
The user will now see a review of the output from the grading system:
-Transcription of Image
-Translation of Transcription
-Grading
  -a letter score using the 5 rank to score
  -a description of whether the attempt was accurate to the english sentence and suggestion
## Sentence Generator LLM Prompt
Generate a simple sentence using the following word: {{word}}
The grammar should be scoped to JLPTN5 grammar
You can use the following vocabulary to construct a simple sentence: 
-simple objects e.g book, car, ramen, shushi
-simple verbs e.g to drink, to eat, to meet
-simple times e.g today, yesterday, tomorrow

## Sentence
use words within the group or just the single target word.

## Grading System
The Grading system will do the following:
-It will transcribe the imgage using MangaOCR
-It will use an LLm to produce a literal translation of the transcription
-It will use another LLm to produce a grade
-It then return this data to the frontend app