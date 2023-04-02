# type: ignore

from sentence_transformers import SentenceTransformer
from tqdm.auto import tqdm
from PyPDF2 import PdfReader
import pinecone, openai
import re, os, shutil
from time import sleep

class Main:

    def __init__(self):
        print('main init')
        self.initialized = False
        self.uploaded = True
        self.model = SentenceTransformer('sentence-transformers/multi-qa-mpnet-base-dot-v1')

        openai.api_key = os.environ.get("OPENAI_KEY")
        pinecone.init(
            api_key=os.environ.get("PINECONE_API_KEY"),
            environment='eu-west1-gcp',
        )
        index_name = os.environ.get("PINECONE_INDEX_NAME")
        ###

        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                index_name,
                dimension=768,
                metric='dotproduct',
                metadata_config={'indexed': []}
            )

        ## GET INDEX
        self.index = pinecone.Index(index_name)
        self.initialized = True
        print(self.index.describe_index_stats())
        
    def uploadDocuments(self, upload_folder):
        while not self.initialized:
            print(f'initialized: {self.initialized}')
            sleep(3)

        self.uploaded = False
        for filename in os.listdir(upload_folder):
            total_vectors = self.index.describe_index_stats()['total_vector_count']
            f = filename.split('.')
            title = ''.join(f[:-1])

            if(f[-1] != 'pdf'):
                raise NotImplementedError

            path = f'{upload_folder}/{filename}'
            sentences = getCorpus(path)
            try:
                shutil.move(path, 'used_data')
            except:
                os.remove(path)

            #   shutil.move(path, 'used_data')

            #   try:
            #     shutil.move(path, 'used_data')
            #   except: 
            #     pass
        
        
            print(f'Vectors for {title}:', len(sentences))

            ids = list(map(str, [*range(total_vectors, total_vectors + len(sentences))]))
            embeds = [self.model.encode(sentence, convert_to_numpy=True).tolist() for sentence in sentences]
            meta = [{'title': title, 'text': sentence} for sentence in sentences]

            to_upsert = list(zip(ids, embeds, meta))
            # print(to_upsert[0])
            self.index.upsert(vectors=to_upsert)
        
        self.uploaded = True

    def query(self, queryText):
        while not self.initialized and not self.uploaded:
            print(f'initialized: {self.initialized} | uploaded: {self.uploaded}')
            sleep(3)

        query = queryText
        qv = self.model.encode(query).tolist()

        completionResult = self.index.query(qv, top_k=3, include_metadata=True)
        # print(res)
        
        contexts = [x['metadata']['text'] for x in completionResult['matches']]
        prompt_start = (
            "Answer the question based on the context below.\n\n"+
            "Context:\n"
        )
        prompt_end = (
            f"\n\nQuestion: {query}\nAnswer:"
        )
        prompt = ''
        limit = 3750
        for i in range(1, len(contexts)):
            if len("\n\n---\n\n".join(contexts[:i])) >= limit:
                prompt = (
                    prompt_start +
                    "\n\n---\n\n".join(contexts[:i-1]) +
                    prompt_end
                )
                break
            elif i == len(contexts)-1:
                prompt = (
                    prompt_start +
                    "\n\n---\n\n".join(contexts) +
                    prompt_end
                )

        # print(prompt)

        completionResult = openai.Completion.create(
            engine='text-davinci-003',
            prompt=prompt,
            temperature=0,
            max_tokens=400,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )
        ans = completionResult['choices'][0]['text'].strip()
        # print('*********************************************************')
        # print(ans)
        return ans




def getCorpus(path):
    pdf_file = open(path, 'rb')
    pdf_reader = PdfReader(pdf_file)
    num_pages = len(pdf_reader.pages)

    text = ''
    for i in range(num_pages):
        page = pdf_reader.pages[i]
        text += page.extract_text()

    pdf_file.close()

    text = text.lower()
    text = text.replace('-\n', '')
    sentences = re.split(r'\.\n', text.split('references\n')[0])

    for i in range(len(sentences)):
      sentences[i] = re.sub(r'[^ -~]', ' ', sentences[i])

    for s in sentences:
      if len(s) < 10:
        sentences.remove(s)
    return sentences

