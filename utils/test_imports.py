# test_imports.py
def test_imports():
    try:
        from utils.file_processors import process_image, process_pdf, process_video
        print("✅ File processors imported successfully")
    except ImportError as e:
        print(f"❌ Error importing file processors: {str(e)}")

    try:
        from utils.model_utils import initialize_model, create_conversation_chain
        print("✅ Model utils imported successfully")
    except ImportError as e:
        print(f"❌ Error importing model utils: {str(e)}")

    try:
        from utils.astra_utils import initialize_embeddings, initialize_astra
        print("✅ Astra utils imported successfully")
    except ImportError as e:
        print(f"❌ Error importing astra utils: {str(e)}")

if __name__ == "__main__":
    test_imports()