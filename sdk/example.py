from sdk import KnowledgeClient

client = KnowledgeClient("http://localhost:8000")

print("===Health===")
print(client.health())

print("\n===Upload===")
result = client.upload("storage/documents/d471fb7e-a899-41dc-a406-fb02e7f51bee_Grades OJT Project 1.1.pdf")
print(result)

print("\n===Upload (again, expect duplicate) ===")
result_dup = client.upload("storage/documents/d471fb7e-a899-41dc-a406-fb02e7f51bee_Grades OJT Project 1.1.pdf")
print(result_dup)
if result_dup.get("duplicate"):
    print("Correctly detected as duplicate — no reprocessing occurred.")

print("\n===List Documents===")
docs = client.list_documents()
for doc in docs:
    print(doc)


print("\n===Ask===")
response = client.ask("who got the highest score?")
