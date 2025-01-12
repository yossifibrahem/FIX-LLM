from duckduckgo_search import DDGS

class DuckDuckGoSearchManager:
    """
    A class to perform various types of web searches using DuckDuckGo.
    """

    def text_search(self, query, num_results=3) -> list:
        """
        Performs a DuckDuckGo text search and returns a list of URLs.

        Parameters:
        - query (str): The search query string for finding relevant text results.
        - num_results (int): The maximum number of URLs to return. Defaults to 3.

        Returns:
        - list of str: A list containing the URLs of the search results. Each URL in the list corresponds to a page that matches the search query.
        """
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=num_results)
            urls = [result['href'] for result in results]
            return urls

    def news_search(self, query, num_results=3) -> list:
        """
        Performs a DuckDuckGo news search and returns a list of news article URLs.

        Parameters:
        - query (str): The search query string for finding relevant news articles.
        - num_results (int): The maximum number of news article URLs to return. Defaults to 3.

        Returns:
        - list of str: A list containing the URLs of the news articles. Each URL in the list corresponds to a news article that matches the search query.
        """
        with DDGS() as ddgs:
            results = ddgs.news(query, max_results=num_results)
            urls = [result['url'] for result in results]
            return urls

    def images_search(self, query, num_results=3) -> list:
        """
        Performs a DuckDuckGo image search and returns a list of dictionaries, each containing URLs for an image and its thumbnail.

        Parameters:
        - query (str): The search query for the image search.
        - num_results (int): The maximum number of image results to return. Defaults to 3.

        Returns:
        - list of dict: A list where each element is a dictionary with two keys:
            'image': URL of the actual image,
            'thumbnail': URL of the thumbnail of the image.
        """
        with DDGS() as ddgs:
            results = ddgs.images(query, max_results=num_results)
            # Extract image and thumbnail URLs
            image_info = [{'image': result['image'], 'thumbnail': result['thumbnail']} for result in results]
            return image_info

    def videos_search(self, query, num_results=3):
        """
        Performs a DuckDuckGo videos search and returns a list of dictionaries, each containing the title and content URL of a video.

        Parameters:
        - query (str): The search query string for finding relevant video results.
        - num_results (int): The maximum number of video results to return. Defaults to 3.

        Returns:
        - list of dict: A list where each dictionary contains 'title' and 'content' keys.
          'title' is the title of the video, and 'content' is the URL of the video.
        """
        with DDGS() as ddgs:
            results = ddgs.videos(query, max_results=num_results)
            video_info = [{'title': result['title'], 'content': result['content']} for result in results]
            return video_info

    def maps_search(self, query, place, num_results=3):
        """
        Performs a DuckDuckGo maps search for a specific query and place, returning a list of relevant location details.

        Parameters:
        - query (str): The search query string for finding relevant map results.
        - place (str): The geographical area or location to focus the search on.
        - num_results (int): The maximum number of results to return. Defaults to 3.

        Returns:
        - list of dict: A list where each dictionary contains the following keys:
            'title': The name or title of the location.
            'address': The address of the location.
            'phone': The phone number of the location, if available.
            'url': The URL to more information about the location.
            'operating_hours': The operating hours of the location, if available.

        Each dictionary represents one map search result, providing concise details about a location relevant to the search query.
        """
        with DDGS() as ddgs:
            results = ddgs.maps(query, place, max_results=num_results)
            map_info = [{'title': result['title'],
                         'address': result['address'],
                         'phone': result.get('phone', 'Not available'),
                         'url': result.get('url', 'Not available'),
                         'operating_hours': result.get('hours', 'Not available')} for result in results]
            return map_info


# if __name__ == "__main__":
#     ddg_search = DuckDuckGoSearchManager()

#     # Example usage:
#     text_results = ddg_search.text_search("Is there any possibility of rain in Berlin today?", 3)
#     print("Text Search Results:", json.dumps(text_results, indent=2, sort_keys=True))

#     news_results = ddg_search.news_search("Is there any possibility of rain in Berlin today?", 3)
#     print("News Search Results:", json.dumps(news_results, indent=2, sort_keys=True))

#     images_results = ddg_search.images_search("puppies", 3)
#     print("Image Search Results:", json.dumps(images_results, indent=2, sort_keys=True))

#     videos_results = ddg_search.videos_search("puppies", 3)
#     print("Video Search Results:", json.dumps(videos_results, indent=2, sort_keys=True))

#     maps_results = ddg_search.maps_search("school", "berlin", 3)
#     print("Maps Search Results:", json.dumps(maps_results, indent=2, sort_keys=True))
