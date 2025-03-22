# Backend API Routes for Frontend Integration

## Overview

This backend code was created to integrate missing API routes into an existing frontend. The work was based on a plan document (`study_sessions.md`), which outlined the necessary routes and their expected functionality. The goal was to fill in the missing routes and ensure smooth interaction with the frontend. Additionally, a test file was created to verify that all routes are working as expected.

## Technical Difficulties

While developing the backend, I encountered several challenges. The main issue was that the AI tool (Cursor) I used to help create the backend code often deviated from the plan specified in the `study_sessions.md` document. To overcome this, I had to constantly remind the tool to follow the plan/template and ensure that the code met the specifications.

Despite this issue, I was able to recreate the necessary backend API routes, test them, and integrate them with the frontend successfully.

## Features

- **Missing API Routes Added**: The core task was to implement the missing API routes as outlined in the `study_sessions.md` document under plans.
- **Test File**: A comprehensive test file was added to verify the functionality of the newly implemented routes.
- **Integration**: Ensured the backend is fully integrated with the frontend codebase to enable seamless communication between the two.

## Test code
The tests codes are located in the tests folder


## Seed code

  {
    "name": "Flashcards",
    "url": "http://localhost:8080/flashcards",
    "preview_url": "http://localhost:8080/flashcards/preview"
  },
  {
    "name": "Quiz",
    "url": "http://localhost:8080/quiz",
    "preview_url": "http://localhost:8080/quiz/preview"
  },