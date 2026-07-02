# Use official Nginx image
FROM nginx:1.25-alpine

# Remove default Nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/

# Copy static files
COPY public/ /usr/share/nginx/html/

# Expose port 80
EXPOSE 80

# Nginx runs in foreground by default
CMD ["nginx", "-g", "daemon off;"]
