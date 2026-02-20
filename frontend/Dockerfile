# Frontend Dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package.json ./
COPY server.js ./
COPY index.html ./
EXPOSE 5173
CMD ["npm", "start"]
