"""
Script complet de validation et réindexation avec chunking par séparateurs
À exécuter avant de démarrer le chatbot
"""

import sys
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from src.embeddings import EmbeddingManager
from src.vector_store import VectorStore
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pattern pour les séparateurs
SEPARATOR_PATTERN = re.compile(r'\n\s*\*{4,}\s*\n')


def extract_sections(text: str):
    """Extract sections based on headers"""
    sections = []
    current_section = {"title": "Introduction", "content": ""}
    
    for line in text.split('\n'):
        if line.strip().startswith('#'):
            if current_section["content"].strip():
                sections.append(current_section)
            title = line.strip().lstrip('#').strip()
            current_section = {"title": title, "content": ""}
        else:
            current_section["content"] += line + "\n"
    
    if current_section["content"].strip():
        sections.append(current_section)
    
    # Si pas de sections, créer une section par défaut
    if not sections:
        sections = [{"title": "Document Content", "content": text}]
    
    return sections


def chunk_by_separator(text: str):
    """Chunk text by separator patterns"""
    if not text or not text.strip():
        return []
    
    chunks = SEPARATOR_PATTERN.split(text)
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    
    return chunks


def validate_and_reindex():
    """Validate documents and reindex with separator chunking"""
    print("=" * 70)
    print("🔍 VALIDATION ET RÉINDEXATION AVEC CHUNKING PAR SÉPARATEURS")
    print("=" * 70)
    
    # 1. Vérifier que le dossier existe
    docs_path = Path(Config.DOCS_FOLDER)
    if not docs_path.exists():
        print(f"\n❌ Dossier non trouvé: {Config.DOCS_FOLDER}")
        print("Veuillez créer le dossier et ajouter vos fichiers .md ou .txt")
        return False
    
    # 2. Lister les fichiers
    md_files = list(docs_path.glob("*.md")) + list(docs_path.glob("*.txt"))
    
    if not md_files:
        print(f"\n❌ Aucun fichier .md ou .txt trouvé dans {Config.DOCS_FOLDER}")
        return False
    
    print(f"\n📄 {len(md_files)} fichier(s) trouvé(s)")
    
    # 3. Valider chaque fichier
    print("\n" + "=" * 70)
    print("PHASE 1: VALIDATION DES DOCUMENTS")
    print("=" * 70)
    
    valid_files = []
    invalid_files = []
    
    for doc_file in md_files:
        print(f"\n📖 {doc_file.name}")
        print("-" * 70)
        
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"  Taille: {len(content)} caractères")
        
        # Chercher les séparateurs
        separators = SEPARATOR_PATTERN.findall(content)
        separator_count = len(separators)
        expected_chunks = separator_count + 1 if separator_count > 0 else 0
        
        print(f"  Séparateurs trouvés: {separator_count}")
        print(f"  Chunks attendus: {expected_chunks}")
        
        if separator_count > 0:
            print(f"  ✅ VALIDE - Document correctement formaté")
            valid_files.append(doc_file)
            
            # Afficher un exemple de séparateur
            if separators:
                print(f"  Exemple de séparateur: {repr(separators[0][:20])}")
        else:
            print(f"  ❌ INVALIDE - Aucun séparateur (****) trouvé!")
            print(f"  ")
            print(f"  Vos documents doivent contenir des lignes comme:")
            print(f"    ****")
            print(f"    *****")
            print(f"    ******")
            print(f"  ")
            print(f"  Aperçu du contenu:")
            print(f"  {content[:300]}")
            invalid_files.append(doc_file)
    
    # 4. Résumé de validation
    print("\n" + "=" * 70)
    print("RÉSUMÉ DE VALIDATION")
    print("=" * 70)
    print(f"✅ Fichiers valides: {len(valid_files)}")
    print(f"❌ Fichiers invalides: {len(invalid_files)}")
    
    if invalid_files:
        print("\nFichiers invalides:")
        for f in invalid_files:
            print(f"  - {f.name}")
        print("\n⚠️  Veuillez ajouter des séparateurs (****) dans ces fichiers avant de continuer.")
    
    if not valid_files:
        print("\n❌ ERREUR: Aucun fichier valide trouvé!")
        print("Impossible de continuer avec la réindexation.")
        return False
    
    # 5. Demander confirmation
    print("\n" + "=" * 70)
    response = input(f"\n🚀 Continuer avec la réindexation de {len(valid_files)} fichier(s) valide(s)? (o/n): ")
    
    if response.lower() != 'o':
        print("❌ Réindexation annulée")
        return False
    
    # 6. Réindexation
    print("\n" + "=" * 70)
    print("PHASE 2: RÉINDEXATION")
    print("=" * 70)
    
    try:
        # Initialiser les composants
        print("\n🔧 Initialisation des composants...")
        embedding_manager = EmbeddingManager(Config.EMBEDDING_MODEL)
        vector_store = VectorStore(Config.CHROMA_DB_PATH)
        
        # Créer une nouvelle collection
        print("📦 Création d'une nouvelle base de données vectorielle...")
        collection = vector_store.create_collection(reset=True)
        
        all_chunks = []
        all_metadatas = []
        total_chunks = 0
        
        # Traiter chaque fichier valide
        for doc_file in valid_files:
            print(f"\n📖 Traitement: {doc_file.name}")
            
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extraire les sections
            sections = extract_sections(content)
            print(f"  Sections trouvées: {len(sections)}")
            
            # Chunker chaque section
            for section in sections:
                section_title = section["title"]
                section_content = section["content"]
                
                if not section_content.strip():
                    continue
                
                # Chunking par séparateurs
                chunks = chunk_by_separator(section_content)
                
                if not chunks:
                    print(f"  ⚠️  Section '{section_title}': Aucun chunk créé")
                    continue
                
                print(f"  Section '{section_title}': {len(chunks)} chunks")
                
                # Ajouter les chunks
                for i, chunk in enumerate(chunks):
                    if not chunk.strip():
                        continue
                    
                    all_chunks.append(chunk)
                    
                    # Créer les métadonnées
                    first_line = chunk.split('\n')[0][:100]
                    metadata = {
                        "document": doc_file.stem,
                        "section": section_title,
                        "chunk_index": i,
                        "chunk_preview": first_line,
                        "chunk_length": len(chunk),
                        "source_file": doc_file.stem
                    }
                    all_metadatas.append(metadata)
                    total_chunks += 1
        
        if not all_chunks:
            print("\n❌ ERREUR: Aucun chunk créé!")
            return False
        
        print(f"\n✅ Total de chunks créés: {total_chunks}")
        
        # Générer les embeddings
        print(f"\n🔢 Génération des embeddings pour {len(all_chunks)} chunks...")
        embeddings = embedding_manager.encode_batch(all_chunks)
        print(f"✅ {len(embeddings)} embeddings générés")
        
        # Ajouter à la base vectorielle
        print("\n💾 Ajout des chunks à la base de données vectorielle...")
        vector_store.add_documents(all_chunks, all_metadatas, embeddings)
        
        # Vérification finale
        final_count = collection.count()
        print(f"\n✅ Base de données créée avec {final_count} chunks!")
        
        # Test de récupération
        print("\n" + "=" * 70)
        print("PHASE 3: TEST DE RÉCUPÉRATION")
        print("=" * 70)
        
        test_query = "Quels sont vos services?"
        print(f"\n🧪 Requête test: '{test_query}'")
        
        query_embedding = embedding_manager.encode(test_query)
        results = vector_store.query(query_embedding, n_results=3)
        
        if results['documents'] and results['documents'][0]:
            print(f"✅ Récupération réussie: {len(results['documents'][0])} chunks")
            
            print("\n📊 Top 3 résultats:")
            for i, (doc, meta, dist) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                print(f"\n  Résultat {i+1}:")
                print(f"    Distance: {dist:.4f}")
                print(f"    Document: {meta.get('document', 'N/A')}")
                print(f"    Section: {meta.get('section', 'N/A')}")
                print(f"    Aperçu: {doc[:150]}...")
        else:
            print("❌ Test échoué: Aucun chunk récupéré!")
            return False
        
        print("\n" + "=" * 70)
        print("✅ RÉINDEXATION TERMINÉE AVEC SUCCÈS!")
        print("=" * 70)
        print(f"\n📊 Statistiques finales:")
        print(f"  - Fichiers traités: {len(valid_files)}")
        print(f"  - Chunks indexés: {final_count}")
        print(f"  - Base de données: {Config.CHROMA_DB_PATH}")
        print(f"\n🚀 Vous pouvez maintenant démarrer votre chatbot!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR durant la réindexation: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = validate_and_reindex()
    sys.exit(0 if success else 1)