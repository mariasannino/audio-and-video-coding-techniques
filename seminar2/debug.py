try:
    print("Trying to import app.py...")
    import app
    print("✓ Import successful")
    
    print("\nTrying to run the app...")
    app.app.run(debug=True, port=5000)
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
