# Language Learning Portal - Frontend

This is the frontend for the Language Learning Portal application, built with React, TypeScript, and Tailwind CSS.

## Docker Implementation

The frontend is fully dockerized for easy deployment:

- **Automatic Container Building**: The frontend is built and served through Nginx
- **API Proxying**: Nginx is configured to proxy API requests to the backend service
- **Client-side Routing**: Support for React Router is enabled for SPA navigation

### Docker Workflow

1. The frontend container builds the React application with npm
2. Nginx serves the static files and handles routing
3. API requests are automatically proxied to the backend service

## Development Setup

### Running with Docker (Recommended)

```sh
# From the project root directory:
docker-compose up
```

This starts both the frontend and backend containers. The frontend will be available at http://localhost:3000.

### Running Locally (Without Docker)

```sh
# Install dependencies
npm install

# Start development server
npm run dev
```

The development server will start at http://localhost:5173 by default.

## Building for Production

```sh
npm run build
```

This creates a production build in the `dist` directory.

## Features

- **Dashboard**: Overview of learning progress and recent activities
- **Study Activities**: Various learning exercises including flashcards and quizzes
- **Word Management**: Browse and search Japanese vocabulary
- **Group Management**: Organize words into study groups
- **Session Tracking**: Track study sessions and progress

## Backend Integration

The frontend expects the backend API to be available at:

- Docker environment: http://lang-portal-backend:5000
- Local development: http://localhost:5000

API routes are prefixed with `/api` in the frontend code, which is automatically proxied to the backend.

# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react/README.md) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type aware lint rules:

- Configure the top-level `parserOptions` property like this:

```js
export default tseslint.config({
  languageOptions: {
    // other options...
    parserOptions: {
      project: ['./tsconfig.node.json', './tsconfig.app.json'],
      tsconfigRootDir: import.meta.dirname,
    },
  },
})
```

- Replace `tseslint.configs.recommended` to `tseslint.configs.recommendedTypeChecked` or `tseslint.configs.strictTypeChecked`
- Optionally add `...tseslint.configs.stylisticTypeChecked`
- Install [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) and update the config:

```js
// eslint.config.js
import react from 'eslint-plugin-react'

export default tseslint.config({
  // Set the react version
  settings: { react: { version: '18.3' } },
  plugins: {
    // Add the react plugin
    react,
  },
  rules: {
    // other rules...
    // Enable its recommended rules
    ...react.configs.recommended.rules,
    ...react.configs['jsx-runtime'].rules,
  },
})
```
