# Podcast-Episode-Recommender-Embeddings
Using vector embeddings to generate podcast episode recomendations


1. Get raw transcripts into local postgres db
2. preprocess text for each transcript
2. create embeddings for each transcript with openai ada embeddings
3. save embeddings to pinecone db
4. use cosine similarity to deterime episode recomendations