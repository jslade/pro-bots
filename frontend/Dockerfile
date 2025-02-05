# Use the official lightweight Node.js 16 image
FROM node:18-slim

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the files
COPY . .

# Start the app
CMD ["npm", "start"]
