from pytubefix import Search, YouTube
from youtube_transcript_api import YouTubeTranscriptApi

def search_youtube(query: str, max_results: int = 5):
    """
    Performs a YouTube search for a specific query and returns the titles and URLs of the top results.
    
    :param query: The search query string for finding relevant YouTube videos.
    
    :param max_results: The maximum number of results to return. Defaults to 5 if not provided.
    
    :return: A list of dictionaries, where each dictionary represents a search result. Each dictionary contains two keys: 'title', title of the video, and 'url', URL to the video.
    """
    try:
        search = Search(query, 'WEB')  # Added 'WEB' parameter
        return [{'title': video.title, 'url': f'https://www.youtube.com/watch?v={video.video_id}'} 
                for video in search.videos[:max_results]]
    except Exception as e:
        print(f"Error during search: {e}")
        return []
    
def get_video_info(url):
    """
    Extracts the title and description of a YouTube video from its URL.

    :param url: The URL of the YouTube video.
    
    :return: A dictionary containing the 'title', 'content' (description) of the video, 'transcript' (transcription). If an error occurs, it returns a dictionary with an 'error' key containing the error message.
    """
    try:
        video_id = url.split('v=')[1]
        yt = YouTube(url, 'WEB')
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = ' '.join([entry['text'] for entry in transcript])
        except:
            transcript_text = "Transcription not available"
        return {
            "title": yt.title,
            "content": yt.description,
            "transcription": transcript_text
        }
    except Exception as e:
        return {"error": str(e)}
