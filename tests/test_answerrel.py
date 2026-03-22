#pip install sentence-transformers
#pip install pandas
from sentence_transformers import SentenceTransformer
from tests.conftest import traced_agent_chat
import numpy as np
import pandas as pd
import pytest 

#pytest tests/test_answerrel.py -v -s 
"""
Below read the csv file using pd that is data format and then conerts each row to dictionary
"""
model = SentenceTransformer('all-MiniLM-L6-v2')

def readcsvfile():
    df=pd.read_csv("tests/data/test_answer.csv")
    print("CSV file read")
    return df.to_dict(orient="records")

class TestAnswerRelevancy:
    @pytest.mark.parametrize("row",readcsvfile())
    def test_answerrelevancy(self,agent,row):
     # ── Step 1 — call agent ──────────────────────
        result = traced_agent_chat(agent, row["question"])

        # ── Step 2 — extract values ──────────────────
        response  = result.get("response")
        question  = row["question"]
        threshold = row["threshold"]
        expected = row["expected"]

        # ── Step 3 — cosine similarity ───────────────
        embeddings = model.encode([question, response]) #Convert to vectors to number arrays (vectors)
        similarity = np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]) #Calculate cosine similarity
        )

        actual = "pass" if similarity > threshold else "fail" #ternary comparison

        print(f"\n{'='*60}")
        print(f"📋 TEST CASE")
      
       
        assert expected == actual, f"Score {similarity:.2f} is below threshold {threshold} for question: {question}"

