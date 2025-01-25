import numpy as np
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

def get_embedding(text, model="Embed_model"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

def cosine_similarity(vec1, vec2):
    sim =  np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    return sim

def find_most_similar_content(data: list, prompt: str, top_n: int =3):
    """
    Find the most similar content to a given query from a list of data.
    Args:
        data (list): A list of dictionaries, where each dictionary contains a 'content' key with text data and a 'url' key with url source of the text.
        query (str): The query string to compare against the content in the data.
        top_n (int, optional): The number of top similar items to return. Defaults to 3.
    Returns:
        list: A list of the top_n most similar items from the data, sorted by similarity in descending order.
    """
    data = spliting(data)
   
    query_embedding = get_embedding(prompt)
    similarities = []

    for item in data:
        content_embedding = get_embedding(item['citation'])
        similarity = cosine_similarity(query_embedding, content_embedding)
        similarities.append((item, similarity))

    # Sort by similarity in descending order and select the top_n
    similarities.sort(key=lambda x: x[1], reverse=True)
    most_similar = [item[0] for item in similarities[:top_n]]

    return most_similar

def divide_into_chunks(text, chunk_size=250, overlap=25):
    # Split the text into individual words
    words = text.split()
    
    # Calculate the start and end indices for each chunk
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk:  # Ensure that the chunk is not empty (happens at the very end)
            chunks.append(chunk)
    
    return chunks

def spliting(results: list):
# devide list of dict into chunks with form of list of dict
   chunks = []
   for result in results:
      if "content" in result:
         one_site_chunks = []
         one_site_chunks.extend(divide_into_chunks(result["content"]))
         for chunk in one_site_chunks:
               chunks.append({"url": result["url"], "citation": chunk})
   return chunks