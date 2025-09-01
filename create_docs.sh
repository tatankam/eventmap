#!/bin/bash

mkdir -p docs

cat > docs/USER_GUIDE.md << EOF
# User Guide

## Introduction

Welcome to the project! This guide covers setup, running, and troubleshooting.

## Installation

- Requirements
- Setting up environment
- Installing dependencies

## Running

Use Docker Compose from the root directory:

\`\`\`bash
docker compose up --build
\`\`\`

## Usage

Basic workflow and examples.

## Troubleshooting

Common issues and solutions.
EOF

cat > docs/ARCHITECTURE_API.md << EOF
# Architecture and API Reference

## Architecture Overview

Description of backend and frontend components, and data flow.

- Backend modules in backend/app/
- Frontend Streamlit app in frontend/

## API Reference

List of available API endpoints with request/response examples.
EOF

cat > docs/CONTRIBUTING.md << EOF
# Contributing Guide and FAQ

## How to Contribute

- Code style (PEP8)
- Running tests (backend/tests)
- Branching and pull request process

## Reporting Issues

How to report bugs and request features.

## FAQ

- Common questions and answers.
EOF

echo "Simplified docs folder with core markdown files created."
