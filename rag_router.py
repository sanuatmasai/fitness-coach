from fastapi import File, HTTPException, Query, APIRouter, UploadFile
from rag_chain import load_and_split_documents, create_retriever, create_rag_chain
import os

# In-memory storage for retriever for simplicity; in production, use persistent storage
global_retriever = None 
router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/ingest/")
async def ingest_document(file: UploadFile = File(...)):
    global global_retriever
    try:
        file_location = f"temp_{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())
        
        documents = load_and_split_documents(file_location)
        global_retriever = create_retriever(documents)
        os.remove(file_location) # Clean up temp file
        return {"message": "Document ingested successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting document: {str(e)}")

@router.post("/query/")
async def query_rag(question: str):
    global global_retriever
    if global_retriever is None:
        raise HTTPException(status_code=400, detail="No document ingested yet. Please ingest a document first.")
    
    rag_chain = create_rag_chain(global_retriever)
    try:
        answer = rag_chain.invoke(question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying RAG: {str(e)}")