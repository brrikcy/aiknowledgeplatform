from sdk import KnowledgeClient

client = KnowledgeClient("http://localhost:8000")

print("===Health===")
print(client.health())

print("\n===Upload===")
result=client.upload("storage/documents/d471fb7e-a899-41dc-a406-fb02e7f51bee_Grades OJT Project 1.1.pdf")
print(result)


print("\n===List Documents===")
docs = client.list_documents()
for doc in docs:
    print(doc)


print("\n===Ask===")
response=client.ask("who got the highest score?")
print("Intent:", response["intent"])
print("Answer:", response["answer"])

print("\n===Ask Stream===")
for token in client.ask_stream("who are in top 5?"):
    print(token, end="",flush=True)
print()


print("\n===Search===")
results = client.search("Shamvail")
for r in results["results"]:
    print(f"Score: {r['rerank_score']:.4f} | {r['chunk_text'][:80]}...")
