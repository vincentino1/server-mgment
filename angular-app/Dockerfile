#Build
FROM node:22.18 AS build

WORKDIR /app

COPY package*.json ./

RUN npm install 

COPY . .

RUN ng build


# Serve with NGINX

FROM nginx:alpine

COPY --from=builder /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]