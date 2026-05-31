from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ingestion.build_corpus import build_document_corpus

def main():
    print("--- STARTING DOCUMENT INGESTION & CORPUS BUILD ---")
    
    input_dir = Path("data/raw/unstructured")
    output_dir = Path("data/processed")
    
    # Run the corpus builder
    summary = build_document_corpus(input_dir, output_dir)
    
    # Print results
    print(f"Loaded documents: {summary['number_of_documents']}")
    print(f"Created chunks:   {summary['number_of_chunks']}")
    
    print("\nGenerated files:")
    print(f"- {output_dir / 'document_chunks.jsonl'}")
    print(f"- {output_dir / 'document_metadata.jsonl'}")
    print(f"- {output_dir / 'schema_snapshot.json'}")
    
    print("\nDocument type distribution:")
    for doc_type, count in summary["document_types"].items():
        print(f"- {doc_type:<20}: {count}")
        
    print("\n--- DOCUMENT INGESTION COMPLETE ---")

if __name__ == "__main__":
    main()
