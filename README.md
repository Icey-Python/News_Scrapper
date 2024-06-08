# NEWS FEED API README

This is a simple Flask API that serves as a proxy for fetching and serving images and provides a news feed.

## Table of Contents
- Introduction
- Routes
- Usage
- License - MIT

## Introduction
#### API_urls:
- https://news-feed-ke.vercel.app/
- https://news-feed-ke.onrender.com/

This Flask API is designed to provide two main functionalities:
1. **Image Proxy:** It allows you to proxy and serve images from external URLs.
2. **News Feed:** It serves news feed data from a JSON file.

# Routes

## `/`

- **Description:** Returns a simple "Hello" message.
- **Method:** GET

## `/proxy-image`

- **Description:** Proxy for fetching and serving images from a given URL.
- **Method:** GET
- **Query Parameters:**
  - `url` (required): The URL of the image to proxy.

## `/news`

- **Description:** Returns news feed data from a JSON file.
- **Method:** GET

# Usage

You can use this API as follows:

## Proxy an Image:

To proxy an image, make a **GET** request to the `/proxy-image` route with the `url` query parameter set to the URL of the image you want to fetch and serve.

**Example:**

- **GET** https://news-feed-ke.vercel.app/proxy-image?url=https://example.com/image.jpg or https://news-feed-ke.onrender.com/proxy-image?url=https://example.com/image.jpg

## Fetch News Feed

To fetch for a news feed, make a **GET** request to the `/news` route

**Example**
- **GET** https://news-feed-ke.vercel.app/news or https://news-feed-ke.onrender.com/news
  


  
- **Visit this website** [https://news-and-weather.vercel.app/](https://news-and-weather.vercel.app/)
  
# Dependencies

-    **Flask:** Web framework for creating the API.
-    **Flask-CORS:** Extension for handling Cross-Origin Resource Sharing (CORS).
-    **Requests:** Library for making HTTP requests.
-    **JSON:** Library for parsing JSON data.


