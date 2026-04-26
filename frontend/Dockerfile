FROM node:22.22.0-alpine

WORKDIR /app

COPY frontend/package.json /app/package.json
RUN npm install

COPY frontend/index.html /app/index.html
COPY frontend/public /app/public
COPY frontend/src /app/src
COPY frontend/vite.config.js /app/vite.config.js

CMD ["npm", "run", "dev"]
